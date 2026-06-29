import time

import torch
from modules.agents import REGISTRY as agent_REGISTRY
from components.action_selectors import REGISTRY as action_REGISTRY
import torch as th
from utils.HGCN import HGCN
from utils.dynamic_clustering import DynamicSpectralClustering
from utils.clustering_csv_logger import ClusteringCSVLogger
import torch.nn as nn
import os


class HYGMA(nn.Module):
    def __init__(self, scheme, groups, args):
        super(HYGMA, self).__init__()
        self.t_env = 0
        self.args = args
        self.n_agents = args.n_agents
        self.input_shape = self._get_input_shape(scheme)
        self.agent_output_type = args.agent_output_type
        self.action_selector = action_REGISTRY[args.action_selector](args)
        self.hidden_states = None

        # 初始化动态谱聚群
        self.clustering = DynamicSpectralClustering(args.min_clusters, args.max_clusters, args.n_agents)
        self.last_clustering_step = 0
        self.clustering_interval = args.clustering_interval
        self.stability_threshold = args.stability_threshold

        # 初始化分组模式与 agent_groups
        self.grouping_mode = getattr(args, "grouping_mode", "dynamic")
        if self.grouping_mode == "each_alone":
            self.agent_groups = [[i] for i in range(self.n_agents)]  # 每人独立一组
        else:
            self.agent_groups = [list(range(self.n_agents))]  # all_one 或 dynamic 初始同组
        self.last_clustering_info = None

        # Stage 2: 聚类活性统计
        self.clustering_stats = {
            "check_count": 0,       # 聚类检查触发次数
            "update_count": 0,      # 实际分组更新次数
            "total_moved": 0,       # 累计移动 agent 数
            "group_sizes": []       # 每次更新后的 group 大小分布快照
        }

        # Stage 3: 拒绝原因追踪 + 分组多样性
        self.rejection_reasons = {}     # reason → count
        self.group_configs_seen = set()  # frozenset of all unique group configs

        # CSV Logger (延迟初始化，等 seed / map 信息可用时再创建)
        self.clustering_csv = None
        self._csv_logger_initialized = False

        self._build_agents(self.input_shape)
        # 初始化HGCN
        self.hgcn_in_dim = self.input_shape
        self.hgcn_hidden_dim = args.hgcn_hidden_dim
        self.hgcn_num_layers = args.hgcn_num_layers
        self.hgcn_out_dim = self.args.hgcn_out_dim

        self.hgcn = HGCN(
            in_dim=self.hgcn_in_dim,
            hidden_dim=self.hgcn_hidden_dim,
            out_dim=self.hgcn_out_dim,
            num_agents=args.n_agents,
            num_groups=len(self.agent_groups),
            num_layers=self.hgcn_num_layers
        )

        # 参数固定
        self.training_steps = 0
        self.fix_hgcn_steps = args.fix_hgcn_steps
        self.fix_grouping_steps = args.fix_grouping_steps


    def select_actions(self, ep_batch, t_ep, t_env, bs=slice(None), test_mode=False):
        # 保持原有的选择动作逻辑
        avail_actions = ep_batch["avail_actions"][:, t_ep]
        agent_outputs = self.forward(ep_batch, t_ep, t_env, test_mode=test_mode)
        chosen_actions = self.action_selector.select_action(agent_outputs[bs], avail_actions[bs], t_env, test_mode=test_mode)
        return chosen_actions

    def forward(self, ep_batch, t, t_env, test_mode=False):
        self.t_env = t_env
        agent_inputs = self._build_inputs(ep_batch, t)
        avail_actions = ep_batch["avail_actions"][:, t]

        if self.grouping_mode == "dynamic" and not test_mode and self.training_steps >= self.fix_grouping_steps:
            if t_env - self.last_clustering_step >= self.clustering_interval:
                start_time = time.time()
                self.clustering_stats["check_count"] += 1  # Stage 2: 统计聚类检查次数
                # 第一次检查时初始化 CSV logger
                if not self._csv_logger_initialized:
                    try:
                        map_name = self.args.env_args["map_name"]
                    except (TypeError, KeyError):
                        map_name = getattr(self.args.env_args, "map_name", "unknown")
                    mode = self.grouping_mode
                    seed = getattr(self.args, "seed", 0)
                    log_dir = os.path.join("..", "results", "clustering_logs")
                    self.clustering_csv = ClusteringCSVLogger(log_dir, map_name, mode, seed)
                    self._csv_logger_initialized = True
                print(f"Clustering check triggered at t_env: {t_env}, interval = {self.clustering_interval}, "
                      f"Last clustering step: {self.last_clustering_step}, "
                      f"Time since last clustering: {t_env - self.last_clustering_step}")
                print(f"now groups: {self.agent_groups}")

                state_history = self._get_state_history(ep_batch, t)
                groups_updated, new_groups, num_moved, silhouette, n_clusters, reject_reason = self.clustering.update_groups(state_history, self.stability_threshold)

                if groups_updated:
                    self.agent_groups = new_groups
                    self.last_clustering_step = t_env
                    # Stage 2: 统计实际更新
                    self.clustering_stats["update_count"] += 1
                    self.clustering_stats["total_moved"] += num_moved
                    self.clustering_stats["group_sizes"].append([len(g) for g in new_groups]); self.rejection_reasons[reject_reason] = self.rejection_reasons.get(reject_reason, 0) + 1; group_key = tuple(sorted(tuple(sorted(g)) for g in new_groups)); self.group_configs_seen.add(group_key)
                    # 更新HGCN的组信息，但不重置权重
                    self.hgcn.update_groups(len(new_groups))
                    print(
                        f"Groups updated at t_env: {t_env}. Moved agents: {num_moved}/{self.n_agents}, silhouette={silhouette:.3f}, n_clusters={n_clusters}, reason={reject_reason}, diversity={len(self.group_configs_seen)}, new groups: {self.agent_groups}")
                else:
                    self.rejection_reasons[reject_reason] = self.rejection_reasons.get(reject_reason, 0) + 1
                    if num_moved > 0:
                        print(
                            f"Groups unchanged at t_env: {t_env}. Reason: {reject_reason}. Potential moves: {num_moved}/{self.n_agents}, silhouette={silhouette:.3f}")
                    else:
                        print(f"Groups unchanged at t_env: {t_env}. Reason: {reject_reason}. No potential moves, silhouette={silhouette:.3f}")
                clustering_time = time.time() - start_time
                print(f"Clustering at step {t_env} took {clustering_time:.4f} seconds")
                self.last_clustering_info = {
                    "num_groups": len(self.agent_groups),
                    "num_moved": num_moved,
                    "silhouette_score": silhouette,
                    "n_clusters": n_clusters,
                    "rejection_reason": reject_reason,
                    "check_count": self.clustering_stats["check_count"],
                    "update_count": self.clustering_stats["update_count"],
                    "total_moved_cum": self.clustering_stats["total_moved"],
                    "diversity": len(self.group_configs_seen),
                }
                # CSV logging
                self.clustering_csv.log_check(
                    t_env=t_env,
                    check_count=self.clustering_stats["check_count"],
                    update_count=self.clustering_stats["update_count"],
                    groups_updated=groups_updated,
                    num_moved=num_moved,
                    num_groups=len(self.agent_groups),
                    group_sizes=[len(g) for g in self.agent_groups],
                    current_groups=self.agent_groups,
                    silhouette_score=silhouette,
                    n_clusters_chosen=n_clusters,
                    latency_ms=clustering_time * 1000,
                    rejection_reason=reject_reason,
                    stability_threshold=self.stability_threshold,
                    group_diversity_so_far=len(self.group_configs_seen),
                )
            else:
                # 即使未触发 interval，也更新累计统计到 last_clustering_info
                self.last_clustering_info = {
                    "num_groups": len(self.agent_groups),
                    "num_moved": 0,
                    "silhouette_score": None,
                    "n_clusters": len(self.agent_groups),
                    "rejection_reason": "not_checked",
                    "check_count": self.clustering_stats["check_count"],
                    "update_count": self.clustering_stats["update_count"],
                    "total_moved_cum": self.clustering_stats["total_moved"],
                    "diversity": len(self.group_configs_seen),
                }

        # 重塑 agent_inputs，确保其形状适合 HGCN
        agent_inputs = agent_inputs.view(ep_batch.batch_size, self.n_agents, -1)

        start_time = time.time()
        # 创建hypergraph（超图邻接矩阵）
        hypergraph = self._create_hypergraph(self.agent_groups, ep_batch.batch_size)

        # 使用HGCN处理输入
        # HGCN输出的特征只包含组内共享信息，因此后续与原始输入结合
        hgcn_features = self.hgcn(agent_inputs, hypergraph)
        hgcn_time = time.time() - start_time

        # 特征结合：将HGCN特征与原始输入结合
        combined_inputs = th.cat([agent_inputs, hgcn_features], dim=-1)

        # 重塑 combined_inputs 以适应 RNN 的输入要求
        combined_inputs = combined_inputs.view(ep_batch.batch_size * self.n_agents, -1)

        # 使用RNN处理结合后的输入
        agent_outs, self.hidden_states = self.agent(combined_inputs, self.hidden_states)

        # 处理agent输出
        if self.agent_output_type == "pi_logits":
            if getattr(self.args, "mask_before_softmax", True):
                reshaped_avail_actions = avail_actions.reshape(ep_batch.batch_size * self.n_agents, -1)
                agent_outs[reshaped_avail_actions == 0] = -1e10
            agent_outs = th.nn.functional.softmax(agent_outs, dim=-1)
            if not test_mode:
                epsilon_action_num = agent_outs.size(-1)
                if getattr(self.args, "mask_before_softmax", True):
                    epsilon_action_num = reshaped_avail_actions.sum(dim=1, keepdim=True).float()
                agent_outs = ((1 - self.action_selector.epsilon) * agent_outs
                              + th.ones_like(agent_outs) * self.action_selector.epsilon / epsilon_action_num)
                if getattr(self.args, "mask_before_softmax", True):
                    agent_outs[reshaped_avail_actions == 0] = 0.0

        if not test_mode:
            self.training_steps += 1


        return agent_outs.view(ep_batch.batch_size, self.n_agents, -1)

    def _create_hypergraph(self, groups, batch_size):
        """
        创建超图邻接矩阵。超图矩阵描述了组与智能体之间的连接关系，用于超图卷积。
        """
        n_groups = len(groups)
        device = next(self.parameters()).device
        hypergraph = torch.zeros(batch_size, n_groups, self.n_agents, device=device)
        for i, group in enumerate(groups):
            hypergraph[:, i, group] = 1
        return hypergraph

    def _get_state_history(self, ep_batch, t):
        history_length = min(self.args.state_history_length, t + 1)
        start = max(0, t - history_length + 1)
        history = ep_batch["state"][:, start:t + 1]
        return history

    def get_attention_weights(self):
        if hasattr(self.hgcn, 'get_attention_weights'):
            return self.hgcn.get_attention_weights()
        return None

    def init_hidden(self, batch_size):
        self.hidden_states = self.agent.init_hidden().unsqueeze(0).expand(batch_size, self.n_agents, -1)

    def parameters(self):
        return self.agent.parameters()

    def clone(self, scheme, groups, args):
        new_mac = type(self)(scheme, groups, args)
        new_mac.load_state(self)
        return new_mac

    def load_state(self, other_mac):
        self.agent.load_state_dict(other_mac.agent.state_dict())
        if hasattr(self, 'hgcn') and hasattr(other_mac, 'hgcn'):
            self.hgcn.load_state_dict(other_mac.hgcn.state_dict())
        self.agent_groups = [group[:] for group in other_mac.agent_groups]

    def cuda(self):
        self.agent.cuda()

    def save_models(self, path):
        th.save(self.agent.state_dict(), "{}/agent.th".format(path))

    def load_models(self, path):
        self.agent.load_state_dict(th.load("{}/agent.th".format(path), map_location=lambda storage, loc: storage))

    def _build_agents(self, input_shape):
        """
        重新构建智能体，确保输入维度包括HGCN输出的特征。
        """
        self.agent = agent_REGISTRY[self.args.agent](input_shape + self.args.hgcn_out_dim, self.args)

    def _build_inputs(self, batch, t):
        bs = batch.batch_size
        inputs = []
        inputs.append(batch["obs"][:, t])  # 观测
        if self.args.obs_last_action:
            if t == 0:
                inputs.append(th.zeros_like(batch["actions_onehot"][:, t]))
            else:
                inputs.append(batch["actions_onehot"][:, t-1])
        if self.args.obs_agent_id:
            inputs.append(th.eye(self.n_agents, device=batch.device).unsqueeze(0).expand(bs, -1, -1))

        inputs = th.cat([x.reshape(bs * self.n_agents, -1) for x in inputs], dim=1)
        return inputs

    def _get_input_shape(self, scheme):
        input_shape = scheme["obs"]["vshape"]
        if self.args.obs_last_action:
            input_shape += scheme["actions_onehot"]["vshape"][0]
        if self.args.obs_agent_id:
            input_shape += self.n_agents
        return input_shape
# M3 instrumentation checkpoint
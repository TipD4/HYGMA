import json, os

base = 'd:/Project/paper/代码/HYGMA/results/sacred'
for run_id in sorted(os.listdir(base), key=lambda x: int(x) if x.isdigit() else 0):
    info_path = os.path.join(base, run_id, 'info.json')
    if not os.path.exists(info_path):
        continue
    with open(info_path) as f:
        data = json.load(f)

    # Extract values from sacred format
    def get_values(key):
        items = data.get(key, [])
        if not items:
            return []
        if isinstance(items, list) and isinstance(items[0], dict):
            return [x['value'] for x in items]
        return items

    test_returns = get_values('test_return_mean')
    battle_won = get_values('test_battle_won_mean')

    if not test_returns:
        continue
    print(f'Run {run_id}: {len(test_returns)} test points')
    print(f'  test_return_mean: final={test_returns[-1]:.2f}, max={max(test_returns):.2f}, first={test_returns[0]:.2f}')
    print(f'  last 5: {[round(x,1) for x in test_returns[-5:]]}')
    if battle_won:
        print(f'  battle_won_mean: final={battle_won[-1]:.3f}, max={max(battle_won):.3f}')
    print()

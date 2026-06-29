# HYGMA Mechanism Verification — Docker Environment
# Base: CUDA 11.7 + Ubuntu 22.04 (matches local torch==1.13.0+cu117)
# Python 3.9 + PyTorch + scikit-learn + h5py + SMAC

FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git \
    build-essential \
    libopenblas-dev \
    libhdf5-dev \
    libssl-dev \
    python3.9 python3.9-dev python3.9-distutils \
    && rm -rf /var/lib/apt/lists/*

# ---- Python setup ----
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# ---- PyTorch (CUDA 11.7) ----
RUN pip3 install --no-cache-dir \
    torch==1.13.0+cu117 \
    --extra-index-url https://download.pytorch.org/whl/cu117

# ---- Core ML + scientific ----
RUN pip3 install --no-cache-dir \
    numpy==1.24.3 \
    scipy==1.10.1 \
    scikit-learn==1.2.2 \
    matplotlib==3.7.1 \
    pandas==2.0.3 \
    h5py==3.9.0

# ---- SMAC + StarCraft II interface ----
RUN pip3 install --no-cache-dir \
    pysc2==3.0.0 \
    absl-py \
    pygame

# ---- Sacred (experiment tracking) ----
RUN pip3 install --no-cache-dir \
    sacred==0.8.5 \
    docopt==0.6.2 \
    munch \
    jsonpickle \
    GitPython

# ---- Additional HYGMA dependencies ----
RUN pip3 install --no-cache-dir \
    pyyaml==6.0 \
    Pillow \
    requests \
    imageio \
    tensorboard-logger

# ---- Environment variables ----
ENV SC2PATH=/root/StarCraftII
ENV PYTHONPATH=/workspace/src:$PYTHONPATH

# ---- Workspace ----
RUN mkdir -p /workspace /root/StarCraftII /results /data
WORKDIR /workspace

# ---- Entrypoint ----
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

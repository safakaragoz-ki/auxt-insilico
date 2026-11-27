#!/bin/bash
# EXPERIMENTAL and untested: RFAA inference environment for the Arrhenius gpu
# partition (aarch64 + NVIDIA GH200). RFAA's own environment.yaml is x86-64 only.
# The blocking dependency is DGL, which has no current CUDA build for aarch64 and
# is compiled from source here against the cluster's PyTorch module.
# Run inside a job on the gpu partition:
#     interactive -A <project>-gpu -p gpu -n 1 -c 16 --gpus 1 -t 03:00:00
#     bash setup/03_install_gpu_aarch64_EXPERIMENTAL.sh GPU/PyTorch/<version>
# (find the module name with: ml avail pytorch). MSAs are still made on the cpu
# partition with jobs/1_msa.sbatch.
set -eo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../settings.sh"
PT_MODULE=${1:?give the PyTorch module name for the gpu partition, e.g. from: ml avail pytorch}
[ "$(uname -m)" = "aarch64" ] || { echo "Run this on a gpu-partition node (aarch64)."; exit 1; }
ENV="$BASE/envs/rfaa_gpu_aarch64"; mkdir -p "$ENV"
module load "$PT_MODULE"
python -m venv --system-site-packages "$ENV/venv"
source "$ENV/venv/bin/activate"
pip install --no-cache-dir hydra-core==1.3.2 omegaconf==2.3.0 assertpy==1.1 e3nn==0.3.3 opt-einsum-fx==0.1.4 \
    icecream deepdiff networkx scipy tqdm pynvml openbabel-wheel \
    git+https://github.com/NVIDIA/dllogger.git@0540a43971f4a8a16693a9de9de73c1072020769
( cd "$RFAA_DIR/rf2aa/SE3Transformer" && pip install --no-cache-dir --no-deps . )

# DGL from source with CUDA (needs cmake and a CUDA toolkit from the loaded modules)
if ! python -c "import dgl" 2>/dev/null; then
    cd "$ENV" && [ -d dgl ] || git clone --recurse-submodules --branch v2.4.0 --depth 1 https://github.com/dmlc/dgl.git
    cd dgl && mkdir -p build && cd build
    cmake -DUSE_CUDA=ON -DBUILD_GRAPHBOLT=OFF -DBUILD_TORCH=ON .. && make -j 16
    cd ../python && DGLBACKEND=pytorch pip install --no-cache-dir --no-deps .
fi

cat > "$ENV/activate.sh" <<ACT
module load "$PT_MODULE"
source "$ENV/venv/bin/activate"
export DGLBACKEND=pytorch PYTHONNOUSERSITE=1
ACT
cd "$RFAA_DIR"
python - <<'PY'
import torch, dgl
import rf2aa.run_inference
g = dgl.graph(([0, 1], [1, 0])).to("cuda:0")
print("torch", torch.__version__, "dgl", dgl.__version__, "CUDA:", torch.cuda.is_available(), "- DGL graph on GPU OK")
PY

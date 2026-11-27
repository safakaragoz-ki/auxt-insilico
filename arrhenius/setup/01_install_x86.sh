#!/bin/bash
# Install RFAA and its conda environment for the x86-64 cpu partition.
# Run on an x86-64 node with internet access, e.g. inside
#     interactive -A <project>-cpu -p cpu -n 1 -c 8 -t 02:00:00
# or on the login node if `uname -m` prints x86_64 there.
#
# Usage: bash setup/01_install_x86.sh /path/to/RoseTTAFold-All-Atom-main.zip
#        (or without argument to git-clone RFAA from GitHub)
set -eo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../settings.sh"
[ "$(uname -m)" = "x86_64" ] || { echo "Run this on an x86-64 node (cpu partition)."; exit 1; }
mkdir -p "$BASE" "$DB_DIR" "$RUN_DIR" "$CONFIG_DIR" "$MSA_DIR" "$(dirname "$ENV_DIR")"

# 1. RFAA source
if [ ! -d "$RFAA_DIR/rf2aa" ]; then
    if [ -n "$1" ]; then
        tmp=$(mktemp -d); unzip -q "$1" -d "$tmp"; mv "$tmp"/RoseTTAFold-All-Atom* "$RFAA_DIR"; rmdir "$tmp"
    else
        git clone https://github.com/baker-laboratory/RoseTTAFold-All-Atom "$RFAA_DIR"
    fi
fi

# 2. conda environment: pinned upstream file first, slim fallback second
module load "$CONDA_MODULE" 2>/dev/null || true
source "$(conda info --base)/etc/profile.d/conda.sh"
export CONDA_PKGS_DIRS="$BASE/conda_pkgs"      # keep the package cache out of $HOME (30 GiB quota)
if [ ! -d "$ENV_DIR" ]; then
    if ! mamba env create -y -p "$ENV_DIR" -f "$RFAA_DIR/environment.yaml"; then
        echo ">>> pinned environment.yaml did not solve; using the slim environment instead"
        rm -rf "$ENV_DIR"
        mamba env create -y -p "$ENV_DIR" -f "$HERE/env_rfaa_x86_slim.yaml"
    fi
fi
conda activate "$ENV_DIR"
export PYTHONNOUSERSITE=1

# 3. SE3Transformer shipped with RFAA
( cd "$RFAA_DIR/rf2aa/SE3Transformer" && pip install --no-cache-dir --no-deps . )

# 4. cs-blast and legacy BLAST data (needed by input_prep/make_ss.sh for PSIPRED)
cd "$RFAA_DIR"
[ -d csblast-2.2.3 ] || bash install_dependencies.sh
if [ ! -d blast-2.2.26/data ]; then
    wget -q https://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/2.2.26/blast-2.2.26-x64-linux.tar.gz
    mkdir -p blast_tmp && tar -xf blast-2.2.26-x64-linux.tar.gz -C blast_tmp
    mv blast_tmp/blast-2.2.26 blast-2.2.26 && rm -rf blast_tmp blast-2.2.26-x64-linux.tar.gz
fi

# 5. MSA wrapper used by the configs (must live in the RFAA directory)
cp "$HERE/make_msa_arrhenius.sh" "$RFAA_DIR/" && chmod +x "$RFAA_DIR/make_msa_arrhenius.sh"

# 6. self-test
python - <<'PY'
import torch, dgl, hydra, e3nn, openbabel, scipy, networkx, icecream, assertpy, deepdiff
import rf2aa.run_inference
print("torch", torch.__version__, "| dgl", dgl.__version__, "| CUDA available:", torch.cuda.is_available())
print("RFAA imports OK")
PY
for tool in hhblits hhsearch hhfilter psipred psipass2 makemat; do
    command -v $tool >/dev/null && echo "found $tool" || echo "MISSING $tool"
done
echo "Done. Next: sbatch setup/02_download_databases.sbatch"

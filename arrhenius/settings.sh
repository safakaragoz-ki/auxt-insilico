# Settings for the AuxT RFAA reruns on Arrhenius. Edit the first block, then
# every script in this folder reads this file. Do not run it directly.

# ---- edit these ------------------------------------------------------------
PROJECT_CPU="naissXXXX-YY-ZZZ-cpu"     # Slurm account for the cpu partition (see: projinfo)
PROJECT_GPU="naissXXXX-YY-ZZZ-gpu"     # Slurm account for the gpu partition (only for the GPU route)
BASE=/nobackup/proj/disk/CHANGE_ME/auxt_rfaa   # project storage, not $HOME (see: storagequota)
CONDA_MODULE="Miniforge"               # exact name from: ml avail miniforge
# ----------------------------------------------------------------------------

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the auxt-insilico checkout
RFAA_DIR="$BASE/RoseTTAFold-All-Atom"   # RFAA source tree
ENV_DIR="$BASE/envs/rfaa_x86"           # conda environment for the cpu partition (x86-64)
DB_DIR="$BASE/databases"
WEIGHTS="$DB_DIR/RFAA_paper_weights.pt"
RUN_DIR="$BASE/runs"                    # RFAA output_path: models, *_aux.pt, per-job MSA folders
CONFIG_DIR="$BASE/configs"              # generated Hydra configs
MSA_DIR="$BASE/msa"                     # one MSA/template search per unique sequence

export DB_UR30="$DB_DIR/UniRef30_2020_06/UniRef30_2020_06"
export DB_BFD="$DB_DIR/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt"   # optional
DB_TEMPL="$DB_DIR/pdb100_2021Mar03/pdb100_2021Mar03"
export BLASTMAT="$RFAA_DIR/blast-2.2.26/data/"

activate_x86_env() {
    if [ "$(uname -m)" != "x86_64" ]; then
        echo "ERROR: this environment is x86-64 only; you are on $(uname -m). Use the cpu partition." >&2
        return 1
    fi
    module load "$CONDA_MODULE" 2>/dev/null || true
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_DIR"
    export PYTHONNOUSERSITE=1
}

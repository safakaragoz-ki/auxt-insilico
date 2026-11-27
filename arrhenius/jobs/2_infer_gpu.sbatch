#!/bin/bash
#SBATCH -J auxt_rfaa_gpu
#SBATCH -p gpu
#SBATCH -n 1
#SBATCH -c 16
#SBATCH --gpus 1
#SBATCH -t 04:00:00
#SBATCH -o auxt_rfaa_gpu_%A_%a.log
# RFAA inference on the gpu partition (aarch64, GH200). Needs the environment
# from setup/03_install_gpu_aarch64_EXPERIMENTAL.sh; see the README before using.
#     sbatch -A <project>-gpu --array=1-11 jobs/2_infer_gpu.sbatch
set -eo pipefail
source "${SLURM_SUBMIT_DIR:-$PWD}/settings.sh"
source "$BASE/envs/rfaa_gpu_aarch64/activate.sh"
JOB=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$CONFIG_DIR/jobs.txt" | cut -f1)
[ -n "$JOB" ] || { echo "no job with index $SLURM_ARRAY_TASK_ID"; exit 1; }
if [ -s "$RUN_DIR/$JOB.pdb" ]; then echo "$JOB already done"; exit 0; fi
nvidia-smi
cd "$RFAA_DIR"
python -m rf2aa.run_inference --config-path "$CONFIG_DIR" --config-name "$JOB"

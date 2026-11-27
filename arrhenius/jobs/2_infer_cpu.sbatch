#!/bin/bash
#SBATCH -J auxt_rfaa
#SBATCH -p cpu
#SBATCH -n 1
#SBATCH -c 64
#SBATCH -t 24:00:00
#SBATCH -o auxt_rfaa_%A_%a.log
# RFAA inference on the x86-64 cpu partition (no GPU), one array task per job.
# Submit from the arrhenius/ folder after jobs/1_msa.sbatch has finished:
#     sbatch -A <project>-cpu --array=1-11 jobs/2_infer_cpu.sbatch
# Test one small job first:  --array=1   (AuxT314_mono_apo)
set -eo pipefail
source "${SLURM_SUBMIT_DIR:-$PWD}/settings.sh"
activate_x86_env
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-16} MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-16}

JOB=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$CONFIG_DIR/jobs.txt" | cut -f1)
[ -n "$JOB" ] || { echo "no job with index $SLURM_ARRAY_TASK_ID"; exit 1; }
if [ -s "$RUN_DIR/$JOB.pdb" ]; then echo "$JOB already done"; exit 0; fi
echo "== $JOB on $(hostname), $(uname -m), $OMP_NUM_THREADS threads, $(date)"
cd "$RFAA_DIR"
/usr/bin/time -v python -m rf2aa.run_inference --config-path "$CONFIG_DIR" --config-name "$JOB"
ls -l "$RUN_DIR/$JOB.pdb" "$RUN_DIR/${JOB}_aux.pt"

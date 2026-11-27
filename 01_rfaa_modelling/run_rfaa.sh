#!/bin/bash
#SBATCH --job-name=RFAA_inference
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=72:00:00
#SBATCH --output=rfaa_%j.out
#SBATCH --error=rfaa_%j.err
#
# RoseTTAFold All-Atom inference for one AuxT job (Slurm, NIH Biowulf module).
# Usage:  sbatch run_rfaa.sh <config-name>      e.g.  sbatch run_rfaa.sh HH103_mono_IAA
# <config-name> is a YAML file (without .yaml) in $RFAA_CONFIG_DIR.
# Outside Biowulf, replace the "module load" line with your own RFAA installation
# (https://github.com/baker-laboratory/RoseTTAFold-All-Atom).

set -euo pipefail
CONFIG_NAME=${1:?give a config name, e.g. HH103_mono_IAA}
RFAA_CONFIG_DIR=${RFAA_CONFIG_DIR:-$PWD/config/inference}

module load RoseTTAFold/allatom

export PYTHONNOUSERSITE=1
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024"
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-16}

python -m rf2aa.run_inference --config-name "$CONFIG_NAME" --config-path "$RFAA_CONFIG_DIR"

#!/bin/bash
#SBATCH --job-name=RFAA_inference
#SBATCH --partition=gpu            # Use GPU partition
#SBATCH --gres=gpu:a100:1          # Request 1 A100 GPU
#SBATCH --cpus-per-task=16         # Allocate more CPUs for efficiency
#SBATCH --mem=128G                 # Increase memory allocation
#SBATCH --time=72:00:00            # Extend runtime if necessary
#SBATCH --output=rfaa_%j.out       # Save output logs
#SBATCH --error=rfaa_%j.err        # Save error logs

# Load necessary modules
module load RoseTTAFold/allatom

# Set environment variables
export PYTHONNOUSERSITE=1
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024"  # Increase split size for large models
export CUDA_LAUNCH_BLOCKING=1   # Debugging: Prevents async CUDA issues
export OMP_NUM_THREADS=16       # Match CPU allocation for parallelism

# Change to working directory
cd /data/karagozm2/RFAA/

# Enable GPU persistence mode (optional, helps with performance)
nvidia-smi -pm 1

# Run inference
python -m rf2aa.run_inference --config-name protein.yaml --config-path /data/karagozm2/RFAA/config/inference

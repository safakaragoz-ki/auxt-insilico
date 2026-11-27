#!/bin/bash
#SBATCH -J auxt_msa
#SBATCH -p cpu
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 12:00:00
#SBATCH -o auxt_msa_%j.log
# MSA and template search, once per unique sequence (x86-64 only), then copied
# into the per-job folders where rf2aa looks for them, so inference never
# starts a search itself. Submit from the arrhenius/ folder:
#     sbatch -A <project>-cpu jobs/1_msa.sbatch
set -eo pipefail
source "${SLURM_SUBMIT_DIR:-$PWD}/settings.sh"
activate_x86_env
CPUS=${SLURM_CPUS_PER_TASK:-8}

declare -A FASTA_OF
while IFS=$'\t' read -r job tag n; do
    fasta=$(grep -A3 "fasta_file" "$CONFIG_DIR/$job.yaml" | grep -m1 fasta_file | awk '{print $2}')
    FASTA_OF[$tag]=$fasta
done < "$CONFIG_DIR/jobs.txt"

cd "$RFAA_DIR"
for tag in "${!FASTA_OF[@]}"; do
    out="$MSA_DIR/$tag"
    if [ -s "$out/t000_.msa0.a3m" ] && [ -s "$out/t000_.hhr" ] && [ -s "$out/t000_.atab" ]; then
        echo "$tag: search already done"
    else
        mkdir -p "$out"
        ./make_msa_arrhenius.sh "${FASTA_OF[$tag]}" "$out" "$CPUS" 64 "$DB_UR30" "$DB_TEMPL"
    fi
    for f in t000_.msa0.a3m t000_.hhr t000_.atab; do
        [ -s "$out/$f" ] || { echo "ERROR: $out/$f missing; see $out/log"; exit 1; }
    done
done

while IFS=$'\t' read -r job tag n; do
    for chain in $(echo ABCD | cut -c1-"$n" | fold -w1); do
        mkdir -p "$RUN_DIR/$job/$chain"
        cp "$MSA_DIR/$tag"/t000_.msa0.a3m "$MSA_DIR/$tag"/t000_.hhr "$MSA_DIR/$tag"/t000_.atab "$RUN_DIR/$job/$chain/"
    done
done < "$CONFIG_DIR/jobs.txt"
echo "MSAs in place for $(wc -l < "$CONFIG_DIR/jobs.txt") jobs"

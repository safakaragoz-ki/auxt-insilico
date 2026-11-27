#!/bin/bash
#SBATCH -J rfaa_databases
#SBATCH -p cpu
#SBATCH -n 1
#SBATCH -c 8
#SBATCH -t 24:00:00
#SBATCH -o rfaa_databases_%j.log
# Submit from the arrhenius/ folder:
#     sbatch -A <project>-cpu setup/02_download_databases.sbatch
# Downloads RFAA weights, UniRef30 (46 GB) and pdb100 templates (81 GB): about 130 GB
# compressed, roughly 300 GB unpacked. Add BFD=1 for the 272 GB BFD fallback database
# (only searched if UniRef30 returns a shallow alignment):
#     sbatch -A <project>-cpu --export=ALL,BFD=1 setup/02_download_databases.sbatch
# If compute nodes have no internet access, run it on the login node instead:
#     bash setup/02_download_databases.sbatch
set -eo pipefail
source "${SLURM_SUBMIT_DIR:-$PWD}/settings.sh"
mkdir -p "$DB_DIR" && cd "$DB_DIR"

[ -s RFAA_paper_weights.pt ] || wget -c http://files.ipd.uw.edu/pub/RF-All-Atom/weights/RFAA_paper_weights.pt

if [ ! -s UniRef30_2020_06/UniRef30_2020_06_hhm.ffdata ]; then
    wget -c http://wwwuser.gwdg.de/~compbiol/uniclust/2020_06/UniRef30_2020_06_hhsuite.tar.gz
    mkdir -p UniRef30_2020_06 && tar xzf UniRef30_2020_06_hhsuite.tar.gz -C UniRef30_2020_06
    rm UniRef30_2020_06_hhsuite.tar.gz
fi

if [ ! -s pdb100_2021Mar03/pdb100_2021Mar03_pdb.ffdata ]; then
    wget -c https://files.ipd.uw.edu/pub/RoseTTAFold/pdb100_2021Mar03.tar.gz
    tar xzf pdb100_2021Mar03.tar.gz && rm pdb100_2021Mar03.tar.gz
fi

if [ "${BFD:-0}" = "1" ] && [ ! -s "${DB_BFD}_hhm.ffdata" ]; then
    wget -c https://bfd.mmseqs.com/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz
    mkdir -p bfd && tar xzf bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz -C bfd
    rm bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz
fi
ls -lh "$DB_DIR"; du -sh "$DB_DIR"/*

#!/bin/bash
# MSA and template search for RFAA. Same search protocol as the make_msa.sh
# shipped with RFAA (HHblits on UniRef30 at 1e-10/1e-6/1e-3, BFD fallback,
# PSIPRED, HHsearch on pdb100), with three changes for this installation:
#   - SignalP 6 is used only if a licensed copy is registered; otherwise the
#     input sequence is used as is (AuxT has no signal peptide);
#   - the BFD fallback is skipped if the BFD database is not installed;
#   - no hard-coded HH-suite path.
# Arguments (set by rf2aa): fasta, out_dir, n_cpu, mem_GB, sequencedb(unused), template_db

in_fasta="$1"; out_dir="$2"; CPU="$3"; MEM="$4"; DB_TEMPL="$6"
[ -z "$DB_TEMPL" ] && DB_TEMPL="$5"      # rf2aa drops the 5th argument when sequencedb is ""

SCRIPT=$(realpath -s "$0"); export PIPE_DIR=$(dirname "$SCRIPT")
: "${DB_UR30:=$PIPE_DIR/UniRef30_2020_06/UniRef30_2020_06}"
: "${DB_BFD:=$PIPE_DIR/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt}"

mkdir -p "$out_dir/signalp" "$out_dir/hhblits" "$out_dir/log"
trim_fasta="$in_fasta"
if command -v signalp6 >/dev/null 2>&1; then
    signalp6 --fastafile "$in_fasta" --organism other --output_dir "$out_dir/signalp" --format none --mode slow \
        > "$out_dir/log/signalp.log" 2>&1
    [ -s "$out_dir/signalp/processed_entries.fasta" ] && trim_fasta="$out_dir/signalp/processed_entries.fasta"
fi

HHOPTS="-o /dev/null -mact 0.35 -maxfilt 100000000 -neffmax 20 -cov 25 -cpu $CPU -nodiff -realign_max 100000000 -maxseq 1000000 -maxmem $MEM -n 4"
tmp_dir="$out_dir/hhblits"; out_prefix="$out_dir/t000_"

pick() {   # pick <a3m prefix>: filter, then accept the MSA if it is deep enough
    hhfilter -maxseq 100000 -id 90 -cov 75 -i "$1.a3m" -o "$1.id90cov75.a3m"
    hhfilter -maxseq 100000 -id 90 -cov 50 -i "$1.a3m" -o "$1.id90cov50.a3m"
    prev_a3m="$1.id90cov50.a3m"
    n75=$(grep -c "^>" "$1.id90cov75.a3m"); n50=$(grep -c "^>" "$1.id90cov50.a3m")
    if ((n75>2000)); then cp "$1.id90cov75.a3m" "${out_prefix}.msa0.a3m"
    elif ((n50>4000)); then cp "$1.id90cov50.a3m" "${out_prefix}.msa0.a3m"; fi
}

if [ ! -s "${out_prefix}.msa0.a3m" ]; then
    prev_a3m="$trim_fasta"
    for e in 1e-10 1e-6 1e-3; do
        echo "HHblits vs UniRef30, E-value $e"
        [ -s "$tmp_dir/t000_.$e.a3m" ] || hhblits $HHOPTS -d "$DB_UR30" -i "$prev_a3m" -oa3m "$tmp_dir/t000_.$e.a3m" -e $e -v 0
        [ -s "$tmp_dir/t000_.$e.a3m" ] || { echo "ERROR: HHblits produced no alignment (check DB_UR30=$DB_UR30)"; exit 1; }
        pick "$tmp_dir/t000_.$e"
        [ -s "${out_prefix}.msa0.a3m" ] && break
    done
    if [ ! -s "${out_prefix}.msa0.a3m" ] && [ -s "${DB_BFD}_hhm.ffdata" ]; then
        echo "HHblits vs BFD, E-value 1e-3"
        [ -s "$tmp_dir/t000_.1e-3.bfd.a3m" ] || hhblits $HHOPTS -d "$DB_BFD" -i "$prev_a3m" -oa3m "$tmp_dir/t000_.1e-3.bfd.a3m" -e 1e-3 -v 0
        [ -s "$tmp_dir/t000_.1e-3.bfd.a3m" ] && pick "$tmp_dir/t000_.1e-3.bfd"
    fi
    [ -s "${out_prefix}.msa0.a3m" ] || cp "$prev_a3m" "${out_prefix}.msa0.a3m"
fi
echo "MSA depth: $(grep -c '^>' "${out_prefix}.msa0.a3m") sequences"

echo "PSIPRED"
( cd "$out_dir" && "$PIPE_DIR/input_prep/make_ss.sh" "$out_dir/t000_.msa0.a3m" "$out_dir/t000_.ss2" \
    > "$out_dir/log/make_ss.stdout" 2> "$out_dir/log/make_ss.stderr" )

if [ ! -s "$out_dir/t000_.hhr" ]; then
    echo "HHsearch vs pdb100"
    if [ -s "$out_dir/t000_.ss2" ]; then
        cat "$out_dir/t000_.ss2" "$out_dir/t000_.msa0.a3m" > "$out_dir/t000_.msa0.ss2.a3m"
    else
        echo "WARNING: PSIPRED failed (see log/make_ss.stderr); template search runs without predicted secondary structure"
        cp "$out_dir/t000_.msa0.a3m" "$out_dir/t000_.msa0.ss2.a3m"
    fi
    hhsearch -b 50 -B 500 -z 50 -Z 500 -mact 0.05 -cpu $CPU -maxmem $MEM -aliw 100000 -e 100 -p 5.0 \
        -d "$DB_TEMPL" -i "$out_dir/t000_.msa0.ss2.a3m" -o "$out_dir/t000_.hhr" -atab "$out_dir/t000_.atab" -v 0
fi

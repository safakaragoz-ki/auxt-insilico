#!/bin/bash
# Generate all RFAA configs. Run on any node after setup/01_install_x86.sh.
#   bash make_configs.sh                 # revised 314-aa AuxT only (11 jobs)
#   bash make_configs.sh --with-401      # also the original 401-aa sequence (22 jobs)
#   MAXCYCLE=10 bash make_configs.sh     # more recycles
set -eo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/settings.sh"
FASTAS=(--fasta "AuxT314=$REPO/sequences/AuxT_HH103_314aa_notail.fasta")
[ "$1" = "--with-401" ] && FASTAS+=(--fasta "AuxT401=$REPO/sequences/AuxT_HH103_401aa.fasta")
PY=python3; [ -x "$ENV_DIR/bin/python" ] && PY="$ENV_DIR/bin/python"
$PY "$HERE/make_configs.py" --rfaa-dir "$RFAA_DIR" --config-dir "$CONFIG_DIR" --run-dir "$RUN_DIR" \
    --weights "$WEIGHTS" --template-db "$DB_TEMPL" --sequence-db "$DB_UR30" \
    --ligand-dir "$REPO/ligands" --maxcycle "${MAXCYCLE:-4}" "${FASTAS[@]}"

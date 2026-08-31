#!/usr/bin/env bash
set -euo pipefail
CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

[[ -f "$REF" ]] || { echo "Reference not found: $REF" >&2; exit 1; }

# BWA index
if [[ ! -f "${REF}.bwt" && ! -f "${REF}.0123" ]]; then
  bwa index "$REF"
fi

# FASTA index
[[ -f "${REF}.fai" ]] || samtools faidx "$REF"

# GATK sequence dictionary
DICT="${REF%.*}.dict"
[[ -f "$DICT" ]] || gatk CreateSequenceDictionary -R "$REF" -O "$DICT"

echo "Reference indices ready."

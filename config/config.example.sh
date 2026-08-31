#!/usr/bin/env bash
# Example configuration. Replace placeholder paths before use.

WORKDIR="/path/to/project"
REF="/path/to/reference.fa"
FAI="${REF}.fai"
GFF="/path/to/annotation.gff3"
SAMPLE_SHEET="${WORKDIR}/config/samples.tsv"
GROUPS="${WORKDIR}/config/populations.tsv"
CHROMS="${WORKDIR}/config/chromosomes.txt"

# Alignment / BAM processing
BWA_THREADS=16
SAMTOOLS_THREADS=8
BCFTOOLS_THREADS=8

# GATK germline calling
GATK_JAVA_MEM="32g"
GATK_HC_EXTRA_ARGS=""

# Variant filtering
# If empty, the cohort VCF produced by 03_joint_genotyping.sh is used.
RAW_VCF=""
MAF=0.05
MAX_MISSING=0.8
MIN_DP=2
MAX_DP=1000
MIN_QUAL=30
MIN_GQ=0
INDEL_WINDOW=5
ADJACENT_GAP_WINDOW=10

# LD pruning / ADMIXTURE
LD_WINDOW=50
LD_STEP=10
LD_R2=0.2
ADMIXTURE_K_MIN=2
ADMIXTURE_K_MAX=10
ADMIXTURE_THREADS=4

# Window-based population statistics
WINDOW=50000
STEP=5000
TAJIMA_WINDOW=50000

# XP-CLR
XPCLR_MAXSNPS=200
XPCLR_MINSNPS=5

# PSMC
PSMC_MIN_DEPTH=10
PSMC_MAX_DEPTH=100
PSMC_N=25
PSMC_T=5
PSMC_R=5
PSMC_PATTERN="4+30*2+4+6+10"
PSMC_BOOTSTRAPS=100
PSMC_MUTATION_RATE="2.5e-9"
PSMC_GENERATION_TIME=2

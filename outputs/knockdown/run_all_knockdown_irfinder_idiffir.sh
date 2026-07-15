#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${BASE_DIR:-$HOME/bigdata}"
IRFINDER_REF="${IRFINDER_REF:-$BASE_DIR/refDir}"
IDIFFIR_DIR="${IDIFFIR_DIR:-$BASE_DIR/Project1/iDiffIR}"
GTF="${GTF:-Homo_sapiens.GRCh38.111.transcript_only.gtf}"
THREADS="${THREADS:-4}"
MINMAP="${MINMAP:-5}"

echo "[INFO] BASE_DIR=$BASE_DIR"
echo "[INFO] IRFINDER_REF=$IRFINDER_REF"
echo "[INFO] IDIFFIR_DIR=$IDIFFIR_DIR"

echo "[INFO] IRFinder CPEB4_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d CPEB4_K562_KO_1 CPEB4_K562/CPEB4_K562_1_1.fastq.gz CPEB4_K562/CPEB4_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d CPEB4_K562_control_1 CPEB4_K562/CPEB4_K562_control1_1.fastq.gz CPEB4_K562/CPEB4_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d CPEB4_K562_KO_2 CPEB4_K562/CPEB4_K562_2_1.fastq.gz CPEB4_K562/CPEB4_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d CPEB4_K562_control_2 CPEB4_K562/CPEB4_K562_control2_1.fastq.gz CPEB4_K562/CPEB4_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR CPEB4_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/CPEB4_K562_KO_1/Unsorted.bam KO/ CPEB4_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/CPEB4_K562_control_1/Unsorted.bam Data/ CPEB4_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/CPEB4_K562_KO_2/Unsorted.bam KO/ CPEB4_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/CPEB4_K562_control_2/Unsorted.bam Data/ CPEB4_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o CPEB4_K562_result "$GTF" KO/CPEB4_K562_1.bam:KO/CPEB4_K562_2.bam Data/CPEB4_K562_control1.bam:Data/CPEB4_K562_control2.bam

echo "[INFO] IRFinder DAZAP1_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d DAZAP1_HepG2_KO_1 DAZAP1_HepG2/DAZAP1_HepG2_1_1.fastq.gz DAZAP1_HepG2/DAZAP1_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DAZAP1_HepG2_control_1 DAZAP1_HepG2/DAZAP1_HepG2_control1_1.fastq.gz DAZAP1_HepG2/DAZAP1_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DAZAP1_HepG2_KO_2 DAZAP1_HepG2/DAZAP1_HepG2_2_1.fastq.gz DAZAP1_HepG2/DAZAP1_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DAZAP1_HepG2_control_2 DAZAP1_HepG2/DAZAP1_HepG2_control2_1.fastq.gz DAZAP1_HepG2/DAZAP1_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR DAZAP1_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/DAZAP1_HepG2_KO_1/Unsorted.bam KO/ DAZAP1_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/DAZAP1_HepG2_control_1/Unsorted.bam Data/ DAZAP1_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/DAZAP1_HepG2_KO_2/Unsorted.bam KO/ DAZAP1_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/DAZAP1_HepG2_control_2/Unsorted.bam Data/ DAZAP1_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o DAZAP1_HepG2_result "$GTF" KO/DAZAP1_HepG2_1.bam:KO/DAZAP1_HepG2_2.bam Data/DAZAP1_HepG2_control1.bam:Data/DAZAP1_HepG2_control2.bam

echo "[INFO] IRFinder EIF4B_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d EIF4B_K562_KO_1 EIF4B_K562/EIF4B_K562_1_1.fastq.gz EIF4B_K562/EIF4B_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d EIF4B_K562_control_1 EIF4B_K562/EIF4B_K562_control1_1.fastq.gz EIF4B_K562/EIF4B_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d EIF4B_K562_KO_2 EIF4B_K562/EIF4B_K562_2_1.fastq.gz EIF4B_K562/EIF4B_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d EIF4B_K562_control_2 EIF4B_K562/EIF4B_K562_control2_1.fastq.gz EIF4B_K562/EIF4B_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR EIF4B_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/EIF4B_K562_KO_1/Unsorted.bam KO/ EIF4B_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/EIF4B_K562_control_1/Unsorted.bam Data/ EIF4B_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/EIF4B_K562_KO_2/Unsorted.bam KO/ EIF4B_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/EIF4B_K562_control_2/Unsorted.bam Data/ EIF4B_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o EIF4B_K562_result "$GTF" KO/EIF4B_K562_1.bam:KO/EIF4B_K562_2.bam Data/EIF4B_K562_control1.bam:Data/EIF4B_K562_control2.bam

echo "[INFO] IRFinder FMR1_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d FMR1_K562_KO_1 FMR1_K562/FMR1_K562_1_1.fastq.gz FMR1_K562/FMR1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FMR1_K562_control_1 FMR1_K562/FMR1_K562_control1_1.fastq.gz FMR1_K562/FMR1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FMR1_K562_KO_2 FMR1_K562/FMR1_K562_2_1.fastq.gz FMR1_K562/FMR1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FMR1_K562_control_2 FMR1_K562/FMR1_K562_control2_1.fastq.gz FMR1_K562/FMR1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR FMR1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/FMR1_K562_KO_1/Unsorted.bam KO/ FMR1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FMR1_K562_control_1/Unsorted.bam Data/ FMR1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FMR1_K562_KO_2/Unsorted.bam KO/ FMR1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FMR1_K562_control_2/Unsorted.bam Data/ FMR1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o FMR1_K562_result "$GTF" KO/FMR1_K562_1.bam:KO/FMR1_K562_2.bam Data/FMR1_K562_control1.bam:Data/FMR1_K562_control2.bam

echo "[INFO] IRFinder FXR1_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d FXR1_K562_KO_1 FXR1_K562/FXR1_K562_1_1.fastq.gz FXR1_K562/FXR1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR1_K562_control_1 FXR1_K562/FXR1_K562_control1_1.fastq.gz FXR1_K562/FXR1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR1_K562_KO_2 FXR1_K562/FXR1_K562_2_1.fastq.gz FXR1_K562/FXR1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR1_K562_control_2 FXR1_K562/FXR1_K562_control2_1.fastq.gz FXR1_K562/FXR1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR FXR1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/FXR1_K562_KO_1/Unsorted.bam KO/ FXR1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR1_K562_control_1/Unsorted.bam Data/ FXR1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR1_K562_KO_2/Unsorted.bam KO/ FXR1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR1_K562_control_2/Unsorted.bam Data/ FXR1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o FXR1_K562_result "$GTF" KO/FXR1_K562_1.bam:KO/FXR1_K562_2.bam Data/FXR1_K562_control1.bam:Data/FXR1_K562_control2.bam

echo "[INFO] IRFinder FXR2_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d FXR2_K562_KO_1 FXR2_K562/FXR2_K562_1_1.fastq.gz FXR2_K562/FXR2_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR2_K562_control_1 FXR2_K562/FXR2_K562_control1_1.fastq.gz FXR2_K562/FXR2_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR2_K562_KO_2 FXR2_K562/FXR2_K562_2_1.fastq.gz FXR2_K562/FXR2_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d FXR2_K562_control_2 FXR2_K562/FXR2_K562_control2_1.fastq.gz FXR2_K562/FXR2_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR FXR2_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/FXR2_K562_KO_1/Unsorted.bam KO/ FXR2_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR2_K562_control_1/Unsorted.bam Data/ FXR2_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR2_K562_KO_2/Unsorted.bam KO/ FXR2_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/FXR2_K562_control_2/Unsorted.bam Data/ FXR2_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o FXR2_K562_result "$GTF" KO/FXR2_K562_1.bam:KO/FXR2_K562_2.bam Data/FXR2_K562_control1.bam:Data/FXR2_K562_control2.bam

echo "[INFO] IRFinder HNRNPK_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d HNRNPK_HepG2_KO_1 HNRNPK_HepG2/HNRNPK_HepG2_1_1.fastq.gz HNRNPK_HepG2/HNRNPK_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPK_HepG2_control_1 HNRNPK_HepG2/HNRNPK_HepG2_control1_1.fastq.gz HNRNPK_HepG2/HNRNPK_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPK_HepG2_KO_2 HNRNPK_HepG2/HNRNPK_HepG2_2_1.fastq.gz HNRNPK_HepG2/HNRNPK_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPK_HepG2_control_2 HNRNPK_HepG2/HNRNPK_HepG2_control2_1.fastq.gz HNRNPK_HepG2/HNRNPK_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR HNRNPK_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/HNRNPK_HepG2_KO_1/Unsorted.bam KO/ HNRNPK_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPK_HepG2_control_1/Unsorted.bam Data/ HNRNPK_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPK_HepG2_KO_2/Unsorted.bam KO/ HNRNPK_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPK_HepG2_control_2/Unsorted.bam Data/ HNRNPK_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o HNRNPK_HepG2_result "$GTF" KO/HNRNPK_HepG2_1.bam:KO/HNRNPK_HepG2_2.bam Data/HNRNPK_HepG2_control1.bam:Data/HNRNPK_HepG2_control2.bam

echo "[INFO] IRFinder HNRNPLL_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d HNRNPLL_HepG2_KO_1 HNRNPLL_HepG2/HNRNPLL_HepG2_1_1.fastq.gz HNRNPLL_HepG2/HNRNPLL_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPLL_HepG2_control_1 HNRNPLL_HepG2/HNRNPLL_HepG2_control1_1.fastq.gz HNRNPLL_HepG2/HNRNPLL_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPLL_HepG2_KO_2 HNRNPLL_HepG2/HNRNPLL_HepG2_2_1.fastq.gz HNRNPLL_HepG2/HNRNPLL_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPLL_HepG2_control_2 HNRNPLL_HepG2/HNRNPLL_HepG2_control2_1.fastq.gz HNRNPLL_HepG2/HNRNPLL_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR HNRNPLL_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/HNRNPLL_HepG2_KO_1/Unsorted.bam KO/ HNRNPLL_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPLL_HepG2_control_1/Unsorted.bam Data/ HNRNPLL_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPLL_HepG2_KO_2/Unsorted.bam KO/ HNRNPLL_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPLL_HepG2_control_2/Unsorted.bam Data/ HNRNPLL_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o HNRNPLL_HepG2_result "$GTF" KO/HNRNPLL_HepG2_1.bam:KO/HNRNPLL_HepG2_2.bam Data/HNRNPLL_HepG2_control1.bam:Data/HNRNPLL_HepG2_control2.bam

echo "[INFO] IRFinder HNRNPL_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d HNRNPL_K562_KO_1 HNRNPL_K562/HNRNPL_K562_1_1.fastq.gz HNRNPL_K562/HNRNPL_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPL_K562_control_1 HNRNPL_K562/HNRNPL_K562_control1_1.fastq.gz HNRNPL_K562/HNRNPL_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPL_K562_KO_2 HNRNPL_K562/HNRNPL_K562_2_1.fastq.gz HNRNPL_K562/HNRNPL_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HNRNPL_K562_control_2 HNRNPL_K562/HNRNPL_K562_control2_1.fastq.gz HNRNPL_K562/HNRNPL_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR HNRNPL_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/HNRNPL_K562_KO_1/Unsorted.bam KO/ HNRNPL_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPL_K562_control_1/Unsorted.bam Data/ HNRNPL_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPL_K562_KO_2/Unsorted.bam KO/ HNRNPL_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/HNRNPL_K562_control_2/Unsorted.bam Data/ HNRNPL_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o HNRNPL_K562_result "$GTF" KO/HNRNPL_K562_1.bam:KO/HNRNPL_K562_2.bam Data/HNRNPL_K562_control1.bam:Data/HNRNPL_K562_control2.bam

echo "[INFO] IRFinder KHDRBS1_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d KHDRBS1_HepG2_KO_1 KHDRBS1_HepG2/KHDRBS1_HepG2_1_1.fastq.gz KHDRBS1_HepG2/KHDRBS1_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KHDRBS1_HepG2_control_1 KHDRBS1_HepG2/KHDRBS1_HepG2_control1_1.fastq.gz KHDRBS1_HepG2/KHDRBS1_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KHDRBS1_HepG2_KO_2 KHDRBS1_HepG2/KHDRBS1_HepG2_2_1.fastq.gz KHDRBS1_HepG2/KHDRBS1_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KHDRBS1_HepG2_control_2 KHDRBS1_HepG2/KHDRBS1_HepG2_control2_1.fastq.gz KHDRBS1_HepG2/KHDRBS1_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR KHDRBS1_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/KHDRBS1_HepG2_KO_1/Unsorted.bam KO/ KHDRBS1_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/KHDRBS1_HepG2_control_1/Unsorted.bam Data/ KHDRBS1_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/KHDRBS1_HepG2_KO_2/Unsorted.bam KO/ KHDRBS1_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/KHDRBS1_HepG2_control_2/Unsorted.bam Data/ KHDRBS1_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o KHDRBS1_HepG2_result "$GTF" KO/KHDRBS1_HepG2_1.bam:KO/KHDRBS1_HepG2_2.bam Data/KHDRBS1_HepG2_control1.bam:Data/KHDRBS1_HepG2_control2.bam

echo "[INFO] IRFinder PABPC1_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d PABPC1_K562_KO_1 PABPC1_K562/PABPC1_K562_1_1.fastq.gz PABPC1_K562/PABPC1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PABPC1_K562_control_1 PABPC1_K562/PABPC1_K562_control1_1.fastq.gz PABPC1_K562/PABPC1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PABPC1_K562_KO_2 PABPC1_K562/PABPC1_K562_2_1.fastq.gz PABPC1_K562/PABPC1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PABPC1_K562_control_2 PABPC1_K562/PABPC1_K562_control2_1.fastq.gz PABPC1_K562/PABPC1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR PABPC1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/PABPC1_K562_KO_1/Unsorted.bam KO/ PABPC1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PABPC1_K562_control_1/Unsorted.bam Data/ PABPC1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PABPC1_K562_KO_2/Unsorted.bam KO/ PABPC1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PABPC1_K562_control_2/Unsorted.bam Data/ PABPC1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o PABPC1_K562_result "$GTF" KO/PABPC1_K562_1.bam:KO/PABPC1_K562_2.bam Data/PABPC1_K562_control1.bam:Data/PABPC1_K562_control2.bam

echo "[INFO] IRFinder PCBP2_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d PCBP2_HepG2_KO_1 PCBP2_HepG2/PCBP2_HepG2_1_1.fastq.gz PCBP2_HepG2/PCBP2_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PCBP2_HepG2_control_1 PCBP2_HepG2/PCBP2_HepG2_control1_1.fastq.gz PCBP2_HepG2/PCBP2_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PCBP2_HepG2_KO_2 PCBP2_HepG2/PCBP2_HepG2_2_1.fastq.gz PCBP2_HepG2/PCBP2_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PCBP2_HepG2_control_2 PCBP2_HepG2/PCBP2_HepG2_control2_1.fastq.gz PCBP2_HepG2/PCBP2_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR PCBP2_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/PCBP2_HepG2_KO_1/Unsorted.bam KO/ PCBP2_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PCBP2_HepG2_control_1/Unsorted.bam Data/ PCBP2_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PCBP2_HepG2_KO_2/Unsorted.bam KO/ PCBP2_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PCBP2_HepG2_control_2/Unsorted.bam Data/ PCBP2_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o PCBP2_HepG2_result "$GTF" KO/PCBP2_HepG2_1.bam:KO/PCBP2_HepG2_2.bam Data/PCBP2_HepG2_control1.bam:Data/PCBP2_HepG2_control2.bam

echo "[INFO] IRFinder PTBP1_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d PTBP1_K562_KO_1 PTBP1_K562/PTBP1_K562_1_1.fastq.gz PTBP1_K562/PTBP1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PTBP1_K562_control_1 PTBP1_K562/PTBP1_K562_control1_1.fastq.gz PTBP1_K562/PTBP1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PTBP1_K562_KO_2 PTBP1_K562/PTBP1_K562_2_1.fastq.gz PTBP1_K562/PTBP1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d PTBP1_K562_control_2 PTBP1_K562/PTBP1_K562_control2_1.fastq.gz PTBP1_K562/PTBP1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR PTBP1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/PTBP1_K562_KO_1/Unsorted.bam KO/ PTBP1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PTBP1_K562_control_1/Unsorted.bam Data/ PTBP1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PTBP1_K562_KO_2/Unsorted.bam KO/ PTBP1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/PTBP1_K562_control_2/Unsorted.bam Data/ PTBP1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o PTBP1_K562_result "$GTF" KO/PTBP1_K562_1.bam:KO/PTBP1_K562_2.bam Data/PTBP1_K562_control1.bam:Data/PTBP1_K562_control2.bam

echo "[INFO] IRFinder SART3_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d SART3_K562_KO_1 SART3_K562/SART3_K562_1_1.fastq.gz SART3_K562/SART3_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SART3_K562_control_1 SART3_K562/SART3_K562_control1_1.fastq.gz SART3_K562/SART3_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SART3_K562_KO_2 SART3_K562/SART3_K562_2_1.fastq.gz SART3_K562/SART3_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SART3_K562_control_2 SART3_K562/SART3_K562_control2_1.fastq.gz SART3_K562/SART3_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR SART3_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/SART3_K562_KO_1/Unsorted.bam KO/ SART3_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SART3_K562_control_1/Unsorted.bam Data/ SART3_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SART3_K562_KO_2/Unsorted.bam KO/ SART3_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SART3_K562_control_2/Unsorted.bam Data/ SART3_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o SART3_K562_result "$GTF" KO/SART3_K562_1.bam:KO/SART3_K562_2.bam Data/SART3_K562_control1.bam:Data/SART3_K562_control2.bam

echo "[INFO] IRFinder SF3B4_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d SF3B4_HepG2_KO_1 SF3B4_HepG2/SF3B4_HepG2_1_1.fastq.gz SF3B4_HepG2/SF3B4_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SF3B4_HepG2_control_1 SF3B4_HepG2/SF3B4_HepG2_control1_1.fastq.gz SF3B4_HepG2/SF3B4_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SF3B4_HepG2_KO_2 SF3B4_HepG2/SF3B4_HepG2_2_1.fastq.gz SF3B4_HepG2/SF3B4_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SF3B4_HepG2_control_2 SF3B4_HepG2/SF3B4_HepG2_control2_1.fastq.gz SF3B4_HepG2/SF3B4_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR SF3B4_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/SF3B4_HepG2_KO_1/Unsorted.bam KO/ SF3B4_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SF3B4_HepG2_control_1/Unsorted.bam Data/ SF3B4_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SF3B4_HepG2_KO_2/Unsorted.bam KO/ SF3B4_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SF3B4_HepG2_control_2/Unsorted.bam Data/ SF3B4_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o SF3B4_HepG2_result "$GTF" KO/SF3B4_HepG2_1.bam:KO/SF3B4_HepG2_2.bam Data/SF3B4_HepG2_control1.bam:Data/SF3B4_HepG2_control2.bam

echo "[INFO] IRFinder SRSF9_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d SRSF9_HepG2_KO_1 SRSF9_HepG2/SRSF9_HepG2_1_1.fastq.gz SRSF9_HepG2/SRSF9_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SRSF9_HepG2_control_1 SRSF9_HepG2/SRSF9_HepG2_control1_1.fastq.gz SRSF9_HepG2/SRSF9_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SRSF9_HepG2_KO_2 SRSF9_HepG2/SRSF9_HepG2_2_1.fastq.gz SRSF9_HepG2/SRSF9_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SRSF9_HepG2_control_2 SRSF9_HepG2/SRSF9_HepG2_control2_1.fastq.gz SRSF9_HepG2/SRSF9_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR SRSF9_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/SRSF9_HepG2_KO_1/Unsorted.bam KO/ SRSF9_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SRSF9_HepG2_control_1/Unsorted.bam Data/ SRSF9_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SRSF9_HepG2_KO_2/Unsorted.bam KO/ SRSF9_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/SRSF9_HepG2_control_2/Unsorted.bam Data/ SRSF9_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o SRSF9_HepG2_result "$GTF" KO/SRSF9_HepG2_1.bam:KO/SRSF9_HepG2_2.bam Data/SRSF9_HepG2_control1.bam:Data/SRSF9_HepG2_control2.bam

echo "[INFO] IRFinder TARDBP_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d TARDBP_HepG2_KO_1 TARDBP_HepG2/TARDBP_HepG2_1_1.fastq.gz TARDBP_HepG2/TARDBP_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TARDBP_HepG2_control_1 TARDBP_HepG2/TARDBP_HepG2_control1_1.fastq.gz TARDBP_HepG2/TARDBP_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TARDBP_HepG2_KO_2 TARDBP_HepG2/TARDBP_HepG2_2_1.fastq.gz TARDBP_HepG2/TARDBP_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TARDBP_HepG2_control_2 TARDBP_HepG2/TARDBP_HepG2_control2_1.fastq.gz TARDBP_HepG2/TARDBP_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR TARDBP_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/TARDBP_HepG2_KO_1/Unsorted.bam KO/ TARDBP_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TARDBP_HepG2_control_1/Unsorted.bam Data/ TARDBP_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TARDBP_HepG2_KO_2/Unsorted.bam KO/ TARDBP_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TARDBP_HepG2_control_2/Unsorted.bam Data/ TARDBP_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o TARDBP_HepG2_result "$GTF" KO/TARDBP_HepG2_1.bam:KO/TARDBP_HepG2_2.bam Data/TARDBP_HepG2_control1.bam:Data/TARDBP_HepG2_control2.bam

echo "[INFO] IRFinder TIA1_K562"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d TIA1_K562_KO_1 TIA1_K562/TIA1_K562_1_1.fastq.gz TIA1_K562/TIA1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TIA1_K562_control_1 TIA1_K562/TIA1_K562_control1_1.fastq.gz TIA1_K562/TIA1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TIA1_K562_KO_2 TIA1_K562/TIA1_K562_2_1.fastq.gz TIA1_K562/TIA1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TIA1_K562_control_2 TIA1_K562/TIA1_K562_control2_1.fastq.gz TIA1_K562/TIA1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR TIA1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/TIA1_K562_KO_1/Unsorted.bam KO/ TIA1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TIA1_K562_control_1/Unsorted.bam Data/ TIA1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TIA1_K562_KO_2/Unsorted.bam KO/ TIA1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/TIA1_K562_control_2/Unsorted.bam Data/ TIA1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o TIA1_K562_result "$GTF" KO/TIA1_K562_1.bam:KO/TIA1_K562_2.bam Data/TIA1_K562_control1.bam:Data/TIA1_K562_control2.bam

echo "[INFO] IRFinder U2AF2_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d U2AF2_HepG2_KO_1 U2AF2_HepG2/U2AF2_HepG2_1_1.fastq.gz U2AF2_HepG2/U2AF2_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d U2AF2_HepG2_control_1 U2AF2_HepG2/U2AF2_HepG2_control1_1.fastq.gz U2AF2_HepG2/U2AF2_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d U2AF2_HepG2_KO_2 U2AF2_HepG2/U2AF2_HepG2_2_1.fastq.gz U2AF2_HepG2/U2AF2_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d U2AF2_HepG2_control_2 U2AF2_HepG2/U2AF2_HepG2_control2_1.fastq.gz U2AF2_HepG2/U2AF2_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR U2AF2_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/U2AF2_HepG2_KO_1/Unsorted.bam KO/ U2AF2_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/U2AF2_HepG2_control_1/Unsorted.bam Data/ U2AF2_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/U2AF2_HepG2_KO_2/Unsorted.bam KO/ U2AF2_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/U2AF2_HepG2_control_2/Unsorted.bam Data/ U2AF2_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o U2AF2_HepG2_result "$GTF" KO/U2AF2_HepG2_1.bam:KO/U2AF2_HepG2_2.bam Data/U2AF2_HepG2_control1.bam:Data/U2AF2_HepG2_control2.bam

echo "[INFO] IRFinder YBX3_HepG2"
cd "$BASE_DIR/RBP_knockdown"
IRFinder -r "$IRFINDER_REF" -d YBX3_HepG2_KO_1 YBX3_HepG2/YBX3_HepG2_1_1.fastq.gz YBX3_HepG2/YBX3_HepG2_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d YBX3_HepG2_control_1 YBX3_HepG2/YBX3_HepG2_control1_1.fastq.gz YBX3_HepG2/YBX3_HepG2_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d YBX3_HepG2_KO_2 YBX3_HepG2/YBX3_HepG2_2_1.fastq.gz YBX3_HepG2/YBX3_HepG2_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d YBX3_HepG2_control_2 YBX3_HepG2/YBX3_HepG2_control2_1.fastq.gz YBX3_HepG2/YBX3_HepG2_control2_2.fastq.gz

echo "[INFO] iDiffIR YBX3_HepG2"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../RBP_knockdown/YBX3_HepG2_KO_1/Unsorted.bam KO/ YBX3_HepG2_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/YBX3_HepG2_control_1/Unsorted.bam Data/ YBX3_HepG2_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/YBX3_HepG2_KO_2/Unsorted.bam KO/ YBX3_HepG2_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../RBP_knockdown/YBX3_HepG2_control_2/Unsorted.bam Data/ YBX3_HepG2_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o YBX3_HepG2_result "$GTF" KO/YBX3_HepG2_1.bam:KO/YBX3_HepG2_2.bam Data/YBX3_HepG2_control1.bam:Data/YBX3_HepG2_control2.bam

echo "[INFO] IRFinder ARID3A_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d ARID3A_K562_KO_1 ARID3A_K562/ARID3A_K562_1_1.fastq.gz ARID3A_K562/ARID3A_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ARID3A_K562_control_1 ARID3A_K562/ARID3A_K562_control1_1.fastq.gz ARID3A_K562/ARID3A_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ARID3A_K562_KO_2 ARID3A_K562/ARID3A_K562_2_1.fastq.gz ARID3A_K562/ARID3A_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ARID3A_K562_control_2 ARID3A_K562/ARID3A_K562_control2_1.fastq.gz ARID3A_K562/ARID3A_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR ARID3A_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/ARID3A_K562_KO_1/Unsorted.bam KO/ ARID3A_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ARID3A_K562_control_1/Unsorted.bam Data/ ARID3A_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ARID3A_K562_KO_2/Unsorted.bam KO/ ARID3A_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ARID3A_K562_control_2/Unsorted.bam Data/ ARID3A_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o ARID3A_K562_result "$GTF" KO/ARID3A_K562_1.bam:KO/ARID3A_K562_2.bam Data/ARID3A_K562_control1.bam:Data/ARID3A_K562_control2.bam

echo "[INFO] IRFinder DLX1_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d DLX1_K562_KO_1 DLX1_K562/DLX1_K562_1_1.fastq.gz DLX1_K562/DLX1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DLX1_K562_control_1 DLX1_K562/DLX1_K562_control1_1.fastq.gz DLX1_K562/DLX1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DLX1_K562_KO_2 DLX1_K562/DLX1_K562_2_1.fastq.gz DLX1_K562/DLX1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d DLX1_K562_control_2 DLX1_K562/DLX1_K562_control2_1.fastq.gz DLX1_K562/DLX1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR DLX1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/DLX1_K562_KO_1/Unsorted.bam KO/ DLX1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/DLX1_K562_control_1/Unsorted.bam Data/ DLX1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/DLX1_K562_KO_2/Unsorted.bam KO/ DLX1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/DLX1_K562_control_2/Unsorted.bam Data/ DLX1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o DLX1_K562_result "$GTF" KO/DLX1_K562_1.bam:KO/DLX1_K562_2.bam Data/DLX1_K562_control1.bam:Data/DLX1_K562_control2.bam

echo "[INFO] IRFinder ERF_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d ERF_K562_KO_1 ERF_K562/ERF_K562_1_1.fastq.gz ERF_K562/ERF_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ERF_K562_control_1 ERF_K562/ERF_K562_control1_1.fastq.gz ERF_K562/ERF_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ERF_K562_KO_2 ERF_K562/ERF_K562_2_1.fastq.gz ERF_K562/ERF_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ERF_K562_control_2 ERF_K562/ERF_K562_control2_1.fastq.gz ERF_K562/ERF_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR ERF_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/ERF_K562_KO_1/Unsorted.bam KO/ ERF_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ERF_K562_control_1/Unsorted.bam Data/ ERF_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ERF_K562_KO_2/Unsorted.bam KO/ ERF_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ERF_K562_control_2/Unsorted.bam Data/ ERF_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o ERF_K562_result "$GTF" KO/ERF_K562_1.bam:KO/ERF_K562_2.bam Data/ERF_K562_control1.bam:Data/ERF_K562_control2.bam

echo "[INFO] IRFinder HOXB4_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d HOXB4_K562_KO_1 HOXB4_K562/HOXB4_K562_1_1.fastq.gz HOXB4_K562/HOXB4_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB4_K562_control_1 HOXB4_K562/HOXB4_K562_control1_1.fastq.gz HOXB4_K562/HOXB4_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB4_K562_KO_2 HOXB4_K562/HOXB4_K562_2_1.fastq.gz HOXB4_K562/HOXB4_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB4_K562_control_2 HOXB4_K562/HOXB4_K562_control2_1.fastq.gz HOXB4_K562/HOXB4_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR HOXB4_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/HOXB4_K562_KO_1/Unsorted.bam KO/ HOXB4_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB4_K562_control_1/Unsorted.bam Data/ HOXB4_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB4_K562_KO_2/Unsorted.bam KO/ HOXB4_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB4_K562_control_2/Unsorted.bam Data/ HOXB4_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o HOXB4_K562_result "$GTF" KO/HOXB4_K562_1.bam:KO/HOXB4_K562_2.bam Data/HOXB4_K562_control1.bam:Data/HOXB4_K562_control2.bam

echo "[INFO] IRFinder HOXB9_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d HOXB9_K562_KO_1 HOXB9_K562/HOXB9_K562_1_1.fastq.gz HOXB9_K562/HOXB9_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB9_K562_control_1 HOXB9_K562/HOXB9_K562_control1_1.fastq.gz HOXB9_K562/HOXB9_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB9_K562_KO_2 HOXB9_K562/HOXB9_K562_2_1.fastq.gz HOXB9_K562/HOXB9_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d HOXB9_K562_control_2 HOXB9_K562/HOXB9_K562_control2_1.fastq.gz HOXB9_K562/HOXB9_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR HOXB9_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/HOXB9_K562_KO_1/Unsorted.bam KO/ HOXB9_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB9_K562_control_1/Unsorted.bam Data/ HOXB9_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB9_K562_KO_2/Unsorted.bam KO/ HOXB9_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/HOXB9_K562_control_2/Unsorted.bam Data/ HOXB9_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o HOXB9_K562_result "$GTF" KO/HOXB9_K562_1.bam:KO/HOXB9_K562_2.bam Data/HOXB9_K562_control1.bam:Data/HOXB9_K562_control2.bam

echo "[INFO] IRFinder KLF2_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d KLF2_K562_KO_1 KLF2_K562/KLF2_K562_1_1.fastq.gz KLF2_K562/KLF2_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KLF2_K562_control_1 KLF2_K562/KLF2_K562_control1_1.fastq.gz KLF2_K562/KLF2_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KLF2_K562_KO_2 KLF2_K562/KLF2_K562_2_1.fastq.gz KLF2_K562/KLF2_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d KLF2_K562_control_2 KLF2_K562/KLF2_K562_control2_1.fastq.gz KLF2_K562/KLF2_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR KLF2_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/KLF2_K562_KO_1/Unsorted.bam KO/ KLF2_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/KLF2_K562_control_1/Unsorted.bam Data/ KLF2_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/KLF2_K562_KO_2/Unsorted.bam KO/ KLF2_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/KLF2_K562_control_2/Unsorted.bam Data/ KLF2_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o KLF2_K562_result "$GTF" KO/KLF2_K562_1.bam:KO/KLF2_K562_2.bam Data/KLF2_K562_control1.bam:Data/KLF2_K562_control2.bam

echo "[INFO] IRFinder NRF1_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d NRF1_K562_KO_1 NRF1_K562/NRF1_K562_1_1.fastq.gz NRF1_K562/NRF1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d NRF1_K562_control_1 NRF1_K562/NRF1_K562_control1_1.fastq.gz NRF1_K562/NRF1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d NRF1_K562_KO_2 NRF1_K562/NRF1_K562_2_1.fastq.gz NRF1_K562/NRF1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d NRF1_K562_control_2 NRF1_K562/NRF1_K562_control2_1.fastq.gz NRF1_K562/NRF1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR NRF1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/NRF1_K562_KO_1/Unsorted.bam KO/ NRF1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/NRF1_K562_control_1/Unsorted.bam Data/ NRF1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/NRF1_K562_KO_2/Unsorted.bam KO/ NRF1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/NRF1_K562_control_2/Unsorted.bam Data/ NRF1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o NRF1_K562_result "$GTF" KO/NRF1_K562_1.bam:KO/NRF1_K562_2.bam Data/NRF1_K562_control1.bam:Data/NRF1_K562_control2.bam

echo "[INFO] IRFinder SMAD5_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d SMAD5_K562_KO_1 SMAD5_K562/SMAD5_K562_1_1.fastq.gz SMAD5_K562/SMAD5_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SMAD5_K562_control_1 SMAD5_K562/SMAD5_K562_control1_1.fastq.gz SMAD5_K562/SMAD5_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SMAD5_K562_KO_2 SMAD5_K562/SMAD5_K562_2_1.fastq.gz SMAD5_K562/SMAD5_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SMAD5_K562_control_2 SMAD5_K562/SMAD5_K562_control2_1.fastq.gz SMAD5_K562/SMAD5_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR SMAD5_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/SMAD5_K562_KO_1/Unsorted.bam KO/ SMAD5_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SMAD5_K562_control_1/Unsorted.bam Data/ SMAD5_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SMAD5_K562_KO_2/Unsorted.bam KO/ SMAD5_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SMAD5_K562_control_2/Unsorted.bam Data/ SMAD5_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o SMAD5_K562_result "$GTF" KO/SMAD5_K562_1.bam:KO/SMAD5_K562_2.bam Data/SMAD5_K562_control1.bam:Data/SMAD5_K562_control2.bam

echo "[INFO] IRFinder SP1_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d SP1_K562_KO_1 SP1_K562/SP1_K562_1_1.fastq.gz SP1_K562/SP1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SP1_K562_control_1 SP1_K562/SP1_K562_control1_1.fastq.gz SP1_K562/SP1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SP1_K562_KO_2 SP1_K562/SP1_K562_2_1.fastq.gz SP1_K562/SP1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d SP1_K562_control_2 SP1_K562/SP1_K562_control2_1.fastq.gz SP1_K562/SP1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR SP1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/SP1_K562_KO_1/Unsorted.bam KO/ SP1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SP1_K562_control_1/Unsorted.bam Data/ SP1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SP1_K562_KO_2/Unsorted.bam KO/ SP1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/SP1_K562_control_2/Unsorted.bam Data/ SP1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o SP1_K562_result "$GTF" KO/SP1_K562_1.bam:KO/SP1_K562_2.bam Data/SP1_K562_control1.bam:Data/SP1_K562_control2.bam

echo "[INFO] IRFinder TFDP1_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d TFDP1_K562_KO_1 TFDP1_K562/TFDP1_K562_1_1.fastq.gz TFDP1_K562/TFDP1_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TFDP1_K562_control_1 TFDP1_K562/TFDP1_K562_control1_1.fastq.gz TFDP1_K562/TFDP1_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TFDP1_K562_KO_2 TFDP1_K562/TFDP1_K562_2_1.fastq.gz TFDP1_K562/TFDP1_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d TFDP1_K562_control_2 TFDP1_K562/TFDP1_K562_control2_1.fastq.gz TFDP1_K562/TFDP1_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR TFDP1_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/TFDP1_K562_KO_1/Unsorted.bam KO/ TFDP1_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/TFDP1_K562_control_1/Unsorted.bam Data/ TFDP1_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/TFDP1_K562_KO_2/Unsorted.bam KO/ TFDP1_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/TFDP1_K562_control_2/Unsorted.bam Data/ TFDP1_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o TFDP1_K562_result "$GTF" KO/TFDP1_K562_1.bam:KO/TFDP1_K562_2.bam Data/TFDP1_K562_control1.bam:Data/TFDP1_K562_control2.bam

echo "[INFO] IRFinder ZNF384_K562"
cd "$BASE_DIR/TF_knockdown"
IRFinder -r "$IRFINDER_REF" -d ZNF384_K562_KO_1 ZNF384_K562/ZNF384_K562_1_1.fastq.gz ZNF384_K562/ZNF384_K562_1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ZNF384_K562_control_1 ZNF384_K562/ZNF384_K562_control1_1.fastq.gz ZNF384_K562/ZNF384_K562_control1_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ZNF384_K562_KO_2 ZNF384_K562/ZNF384_K562_2_1.fastq.gz ZNF384_K562/ZNF384_K562_2_2.fastq.gz
IRFinder -r "$IRFINDER_REF" -d ZNF384_K562_control_2 ZNF384_K562/ZNF384_K562_control2_1.fastq.gz ZNF384_K562/ZNF384_K562_control2_2.fastq.gz

echo "[INFO] iDiffIR ZNF384_K562"
cd "$IDIFFIR_DIR"
source ~/.bashrc
conda activate idiffir_py2
mkdir -p KO Data
./convertBam.sh ../../TF_knockdown/ZNF384_K562_KO_1/Unsorted.bam KO/ ZNF384_K562_1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ZNF384_K562_control_1/Unsorted.bam Data/ ZNF384_K562_control1.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ZNF384_K562_KO_2/Unsorted.bam KO/ ZNF384_K562_2.bam -p "$THREADS" -m "$MINMAP" -v
./convertBam.sh ../../TF_knockdown/ZNF384_K562_control_2/Unsorted.bam Data/ ZNF384_K562_control2.bam -p "$THREADS" -m "$MINMAP" -v
idiffir.py -e IR -l KnockOut Wildtype -o ZNF384_K562_result "$GTF" KO/ZNF384_K562_1.bam:KO/ZNF384_K562_2.bam Data/ZNF384_K562_control1.bam:Data/ZNF384_K562_control2.bam


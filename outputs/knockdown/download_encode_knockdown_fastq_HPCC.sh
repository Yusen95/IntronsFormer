#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${BASE_DIR:-$HOME/bigdata}"

echo "[INFO] BASE_DIR=$BASE_DIR"

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 KO rep1 read1 ENCFF505RLY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF505RLY/@@download/ENCFF505RLY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 KO rep1 read2 ENCFF074RIY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF074RIY/@@download/ENCFF074RIY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 KO rep2 read1 ENCFF855BLA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF855BLA/@@download/ENCFF855BLA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 KO rep2 read2 ENCFF424DAC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF424DAC/@@download/ENCFF424DAC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ERF_K562"
out="$BASE_DIR/TF_knockdown/ERF_K562/ERF_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ERF_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 KO rep1 read1 ENCFF343HHD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF343HHD/@@download/ENCFF343HHD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 KO rep1 read2 ENCFF542NYJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF542NYJ/@@download/ENCFF542NYJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 KO rep2 read1 ENCFF605PSQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF605PSQ/@@download/ENCFF605PSQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 KO rep2 read2 ENCFF125MSP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF125MSP/@@download/ENCFF125MSP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/KLF2_K562"
out="$BASE_DIR/TF_knockdown/KLF2_K562/KLF2_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KLF2_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 KO rep1 read1 ENCFF662JSD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF662JSD/@@download/ENCFF662JSD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 KO rep1 read2 ENCFF310ZWY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF310ZWY/@@download/ENCFF310ZWY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 KO rep2 read1 ENCFF337RYW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF337RYW/@@download/ENCFF337RYW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 KO rep2 read2 ENCFF210GYE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF210GYE/@@download/ENCFF210GYE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/NRF1_K562"
out="$BASE_DIR/TF_knockdown/NRF1_K562/NRF1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] NRF1_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 KO rep1 read1 ENCFF088VQG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF088VQG/@@download/ENCFF088VQG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 KO rep1 read2 ENCFF494YMY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF494YMY/@@download/ENCFF494YMY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 KO rep2 read1 ENCFF122YKX"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF122YKX/@@download/ENCFF122YKX.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 KO rep2 read2 ENCFF029ACW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF029ACW/@@download/ENCFF029ACW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SMAD5_K562"
out="$BASE_DIR/TF_knockdown/SMAD5_K562/SMAD5_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SMAD5_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 KO rep1 read1 ENCFF185DZU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF185DZU/@@download/ENCFF185DZU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 KO rep1 read2 ENCFF887URQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF887URQ/@@download/ENCFF887URQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 KO rep2 read1 ENCFF433SSS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF433SSS/@@download/ENCFF433SSS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 KO rep2 read2 ENCFF117LIM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF117LIM/@@download/ENCFF117LIM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/SP1_K562"
out="$BASE_DIR/TF_knockdown/SP1_K562/SP1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SP1_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 KO rep1 read1 ENCFF950DEP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF950DEP/@@download/ENCFF950DEP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 KO rep1 read2 ENCFF135TCS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF135TCS/@@download/ENCFF135TCS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 KO rep2 read1 ENCFF319JXL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF319JXL/@@download/ENCFF319JXL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 KO rep2 read2 ENCFF877IJV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF877IJV/@@download/ENCFF877IJV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/TFDP1_K562"
out="$BASE_DIR/TF_knockdown/TFDP1_K562/TFDP1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TFDP1_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 KO rep1 read1 ENCFF815JOK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF815JOK/@@download/ENCFF815JOK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 KO rep1 read2 ENCFF724FVA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF724FVA/@@download/ENCFF724FVA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 KO rep2 read1 ENCFF911DGQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF911DGQ/@@download/ENCFF911DGQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 KO rep2 read2 ENCFF747YIC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF747YIC/@@download/ENCFF747YIC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ARID3A_K562"
out="$BASE_DIR/TF_knockdown/ARID3A_K562/ARID3A_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ARID3A_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 KO rep1 read1 ENCFF900SXQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF900SXQ/@@download/ENCFF900SXQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 KO rep1 read2 ENCFF359NHT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF359NHT/@@download/ENCFF359NHT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 KO rep2 read1 ENCFF706BMS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF706BMS/@@download/ENCFF706BMS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 KO rep2 read2 ENCFF217WNS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF217WNS/@@download/ENCFF217WNS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/DLX1_K562"
out="$BASE_DIR/TF_knockdown/DLX1_K562/DLX1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DLX1_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 KO rep1 read1 ENCFF779EXF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF779EXF/@@download/ENCFF779EXF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 KO rep1 read2 ENCFF320RNF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF320RNF/@@download/ENCFF320RNF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 KO rep2 read1 ENCFF883BWZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF883BWZ/@@download/ENCFF883BWZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 KO rep2 read2 ENCFF446JGK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF446JGK/@@download/ENCFF446JGK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 control rep1 read1 ENCFF112FMQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF112FMQ/@@download/ENCFF112FMQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 control rep1 read2 ENCFF436EDN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF436EDN/@@download/ENCFF436EDN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 control rep2 read1 ENCFF615EBT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF615EBT/@@download/ENCFF615EBT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB4_K562"
out="$BASE_DIR/TF_knockdown/HOXB4_K562/HOXB4_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB4_K562 control rep2 read2 ENCFF692YJK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF692YJK/@@download/ENCFF692YJK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 KO rep1 read1 ENCFF659HXE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF659HXE/@@download/ENCFF659HXE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 KO rep1 read2 ENCFF421NAC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF421NAC/@@download/ENCFF421NAC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 KO rep2 read1 ENCFF568YGM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF568YGM/@@download/ENCFF568YGM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 KO rep2 read2 ENCFF535AXO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF535AXO/@@download/ENCFF535AXO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 control rep1 read1 ENCFF297OZN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF297OZN/@@download/ENCFF297OZN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 control rep1 read2 ENCFF568AEP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF568AEP/@@download/ENCFF568AEP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 control rep2 read1 ENCFF883YZS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF883YZS/@@download/ENCFF883YZS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/HOXB9_K562"
out="$BASE_DIR/TF_knockdown/HOXB9_K562/HOXB9_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HOXB9_K562 control rep2 read2 ENCFF586CLX"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF586CLX/@@download/ENCFF586CLX.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 KO rep1 read1 ENCFF782ARK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF782ARK/@@download/ENCFF782ARK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 KO rep1 read2 ENCFF998LRA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF998LRA/@@download/ENCFF998LRA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 KO rep2 read1 ENCFF249IVS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF249IVS/@@download/ENCFF249IVS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 KO rep2 read2 ENCFF694RBP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF694RBP/@@download/ENCFF694RBP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 control rep1 read1 ENCFF297OZN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF297OZN/@@download/ENCFF297OZN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 control rep1 read2 ENCFF568AEP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF568AEP/@@download/ENCFF568AEP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 control rep2 read1 ENCFF883YZS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF883YZS/@@download/ENCFF883YZS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/TF_knockdown/ZNF384_K562"
out="$BASE_DIR/TF_knockdown/ZNF384_K562/ZNF384_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] ZNF384_K562 control rep2 read2 ENCFF586CLX"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF586CLX/@@download/ENCFF586CLX.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 KO rep1 read1 ENCFF071FYQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF071FYQ/@@download/ENCFF071FYQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 KO rep1 read2 ENCFF313BXR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF313BXR/@@download/ENCFF313BXR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 KO rep2 read1 ENCFF709OSO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF709OSO/@@download/ENCFF709OSO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 KO rep2 read2 ENCFF984IGG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF984IGG/@@download/ENCFF984IGG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 control rep1 read1 ENCFF399RNY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF399RNY/@@download/ENCFF399RNY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 control rep1 read2 ENCFF964LLJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF964LLJ/@@download/ENCFF964LLJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 control rep2 read1 ENCFF546VNH"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF546VNH/@@download/ENCFF546VNH.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/DAZAP1_HepG2"
out="$BASE_DIR/RBP_knockdown/DAZAP1_HepG2/DAZAP1_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] DAZAP1_HepG2 control rep2 read2 ENCFF420URE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF420URE/@@download/ENCFF420URE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 KO rep1 read1 ENCFF591AGR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF591AGR/@@download/ENCFF591AGR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 KO rep1 read2 ENCFF854WET"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF854WET/@@download/ENCFF854WET.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 KO rep2 read1 ENCFF199PVY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF199PVY/@@download/ENCFF199PVY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 KO rep2 read2 ENCFF878CVQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF878CVQ/@@download/ENCFF878CVQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 control rep1 read1 ENCFF791HTS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF791HTS/@@download/ENCFF791HTS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 control rep1 read2 ENCFF691MJX"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF691MJX/@@download/ENCFF691MJX.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 control rep2 read1 ENCFF078MXU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF078MXU/@@download/ENCFF078MXU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FMR1_K562"
out="$BASE_DIR/RBP_knockdown/FMR1_K562/FMR1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FMR1_K562 control rep2 read2 ENCFF656RXL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF656RXL/@@download/ENCFF656RXL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 KO rep1 read1 ENCFF002CAT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAT/@@download/ENCFF002CAT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 KO rep1 read2 ENCFF002CAU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAU/@@download/ENCFF002CAU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 KO rep2 read1 ENCFF002CAV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAV/@@download/ENCFF002CAV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 KO rep2 read2 ENCFF002CAW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAW/@@download/ENCFF002CAW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 control rep1 read1 ENCFF002CAL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAL/@@download/ENCFF002CAL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 control rep1 read2 ENCFF002CAM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAM/@@download/ENCFF002CAM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 control rep2 read1 ENCFF002CAN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAN/@@download/ENCFF002CAN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR2_K562"
out="$BASE_DIR/RBP_knockdown/FXR2_K562/FXR2_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR2_K562 control rep2 read2 ENCFF002CAO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF002CAO/@@download/ENCFF002CAO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 KO rep1 read1 ENCFF106HXI"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF106HXI/@@download/ENCFF106HXI.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 KO rep1 read2 ENCFF763SDA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF763SDA/@@download/ENCFF763SDA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 KO rep2 read1 ENCFF462KWR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF462KWR/@@download/ENCFF462KWR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 KO rep2 read2 ENCFF949CWD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF949CWD/@@download/ENCFF949CWD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 control rep1 read1 ENCFF801YDB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF801YDB/@@download/ENCFF801YDB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 control rep1 read2 ENCFF794CUL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF794CUL/@@download/ENCFF794CUL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 control rep2 read1 ENCFF619LUS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF619LUS/@@download/ENCFF619LUS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPK_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPK_HepG2/HNRNPK_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPK_HepG2 control rep2 read2 ENCFF200OMG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF200OMG/@@download/ENCFF200OMG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 KO rep1 read1 ENCFF201DAB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF201DAB/@@download/ENCFF201DAB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 KO rep1 read2 ENCFF788TCC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF788TCC/@@download/ENCFF788TCC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 KO rep2 read1 ENCFF017PVQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF017PVQ/@@download/ENCFF017PVQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 KO rep2 read2 ENCFF263RWL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF263RWL/@@download/ENCFF263RWL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 control rep1 read1 ENCFF866KCW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF866KCW/@@download/ENCFF866KCW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 control rep1 read2 ENCFF518SUL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF518SUL/@@download/ENCFF518SUL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 control rep2 read1 ENCFF813XBJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF813XBJ/@@download/ENCFF813XBJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PCBP2_HepG2"
out="$BASE_DIR/RBP_knockdown/PCBP2_HepG2/PCBP2_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PCBP2_HepG2 control rep2 read2 ENCFF276KEO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF276KEO/@@download/ENCFF276KEO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 KO rep1 read1 ENCFF515DAB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF515DAB/@@download/ENCFF515DAB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 KO rep1 read2 ENCFF275BLA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF275BLA/@@download/ENCFF275BLA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 KO rep2 read1 ENCFF763ICV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF763ICV/@@download/ENCFF763ICV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 KO rep2 read2 ENCFF391OVD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF391OVD/@@download/ENCFF391OVD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 control rep1 read1 ENCFF025YLM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF025YLM/@@download/ENCFF025YLM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 control rep1 read2 ENCFF697WWV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF697WWV/@@download/ENCFF697WWV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 control rep2 read1 ENCFF317AWM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF317AWM/@@download/ENCFF317AWM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SRSF9_HepG2"
out="$BASE_DIR/RBP_knockdown/SRSF9_HepG2/SRSF9_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SRSF9_HepG2 control rep2 read2 ENCFF023MFT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF023MFT/@@download/ENCFF023MFT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 KO rep1 read1 ENCFF114ZEL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF114ZEL/@@download/ENCFF114ZEL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 KO rep1 read2 ENCFF508IXG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF508IXG/@@download/ENCFF508IXG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 KO rep2 read1 ENCFF123VQY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF123VQY/@@download/ENCFF123VQY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 KO rep2 read2 ENCFF031GRZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF031GRZ/@@download/ENCFF031GRZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 control rep1 read1 ENCFF361RLP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF361RLP/@@download/ENCFF361RLP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 control rep1 read2 ENCFF043VJU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF043VJU/@@download/ENCFF043VJU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 control rep2 read1 ENCFF803FSB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF803FSB/@@download/ENCFF803FSB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/CPEB4_K562"
out="$BASE_DIR/RBP_knockdown/CPEB4_K562/CPEB4_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] CPEB4_K562 control rep2 read2 ENCFF827KTS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF827KTS/@@download/ENCFF827KTS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 KO rep1 read1 ENCFF212RVY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF212RVY/@@download/ENCFF212RVY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 KO rep1 read2 ENCFF438PPS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF438PPS/@@download/ENCFF438PPS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 KO rep2 read1 ENCFF715FJL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF715FJL/@@download/ENCFF715FJL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 KO rep2 read2 ENCFF552XHQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF552XHQ/@@download/ENCFF552XHQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 control rep1 read1 ENCFF711JSH"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF711JSH/@@download/ENCFF711JSH.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 control rep1 read2 ENCFF941XAQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF941XAQ/@@download/ENCFF941XAQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 control rep2 read1 ENCFF701KJC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF701KJC/@@download/ENCFF701KJC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/YBX3_HepG2"
out="$BASE_DIR/RBP_knockdown/YBX3_HepG2/YBX3_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] YBX3_HepG2 control rep2 read2 ENCFF603JIF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF603JIF/@@download/ENCFF603JIF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 KO rep1 read1 ENCFF824FES"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF824FES/@@download/ENCFF824FES.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 KO rep1 read2 ENCFF439RFC"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF439RFC/@@download/ENCFF439RFC.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 KO rep2 read1 ENCFF540OGR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF540OGR/@@download/ENCFF540OGR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 KO rep2 read2 ENCFF745IWF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF745IWF/@@download/ENCFF745IWF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 control rep1 read1 ENCFF017WXT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF017WXT/@@download/ENCFF017WXT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 control rep1 read2 ENCFF510GOL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF510GOL/@@download/ENCFF510GOL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 control rep2 read1 ENCFF767CVZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF767CVZ/@@download/ENCFF767CVZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/EIF4B_K562"
out="$BASE_DIR/RBP_knockdown/EIF4B_K562/EIF4B_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] EIF4B_K562 control rep2 read2 ENCFF791XKE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF791XKE/@@download/ENCFF791XKE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 KO rep1 read1 ENCFF430FYR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF430FYR/@@download/ENCFF430FYR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 KO rep1 read2 ENCFF733UKJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF733UKJ/@@download/ENCFF733UKJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 KO rep2 read1 ENCFF332WAY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF332WAY/@@download/ENCFF332WAY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 KO rep2 read2 ENCFF208GLL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF208GLL/@@download/ENCFF208GLL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 control rep1 read1 ENCFF017WXT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF017WXT/@@download/ENCFF017WXT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 control rep1 read2 ENCFF510GOL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF510GOL/@@download/ENCFF510GOL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 control rep2 read1 ENCFF767CVZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF767CVZ/@@download/ENCFF767CVZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/FXR1_K562"
out="$BASE_DIR/RBP_knockdown/FXR1_K562/FXR1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] FXR1_K562 control rep2 read2 ENCFF791XKE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF791XKE/@@download/ENCFF791XKE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 KO rep1 read1 ENCFF702UDY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF702UDY/@@download/ENCFF702UDY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 KO rep1 read2 ENCFF689XVP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF689XVP/@@download/ENCFF689XVP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 KO rep2 read1 ENCFF909SSA"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF909SSA/@@download/ENCFF909SSA.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 KO rep2 read2 ENCFF730GDK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF730GDK/@@download/ENCFF730GDK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 control rep1 read1 ENCFF366MJN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF366MJN/@@download/ENCFF366MJN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 control rep1 read2 ENCFF259JKZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF259JKZ/@@download/ENCFF259JKZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 control rep2 read1 ENCFF006BJQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF006BJQ/@@download/ENCFF006BJQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2"
out="$BASE_DIR/RBP_knockdown/KHDRBS1_HepG2/KHDRBS1_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] KHDRBS1_HepG2 control rep2 read2 ENCFF271EDI"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF271EDI/@@download/ENCFF271EDI.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 KO rep1 read1 ENCFF673ANB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF673ANB/@@download/ENCFF673ANB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 KO rep1 read2 ENCFF968JSN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF968JSN/@@download/ENCFF968JSN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 KO rep2 read1 ENCFF141GMF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF141GMF/@@download/ENCFF141GMF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 KO rep2 read2 ENCFF380NPY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF380NPY/@@download/ENCFF380NPY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 control rep1 read1 ENCFF447KSW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF447KSW/@@download/ENCFF447KSW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 control rep1 read2 ENCFF111AWS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF111AWS/@@download/ENCFF111AWS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 control rep2 read1 ENCFF497HLJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF497HLJ/@@download/ENCFF497HLJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PABPC1_K562"
out="$BASE_DIR/RBP_knockdown/PABPC1_K562/PABPC1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PABPC1_K562 control rep2 read2 ENCFF561NSL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF561NSL/@@download/ENCFF561NSL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 KO rep1 read1 ENCFF184CDV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF184CDV/@@download/ENCFF184CDV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 KO rep1 read2 ENCFF456OPJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF456OPJ/@@download/ENCFF456OPJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 KO rep2 read1 ENCFF893AGN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF893AGN/@@download/ENCFF893AGN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 KO rep2 read2 ENCFF642KBO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF642KBO/@@download/ENCFF642KBO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 control rep1 read1 ENCFF726LTF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF726LTF/@@download/ENCFF726LTF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 control rep1 read2 ENCFF569YVH"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF569YVH/@@download/ENCFF569YVH.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 control rep2 read1 ENCFF891EGO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF891EGO/@@download/ENCFF891EGO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/PTBP1_K562"
out="$BASE_DIR/RBP_knockdown/PTBP1_K562/PTBP1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] PTBP1_K562 control rep2 read2 ENCFF667EXM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF667EXM/@@download/ENCFF667EXM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 KO rep1 read1 ENCFF610JSB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF610JSB/@@download/ENCFF610JSB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 KO rep1 read2 ENCFF168QLG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF168QLG/@@download/ENCFF168QLG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 KO rep2 read1 ENCFF517FBY"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF517FBY/@@download/ENCFF517FBY.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 KO rep2 read2 ENCFF043UGU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF043UGU/@@download/ENCFF043UGU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 control rep1 read1 ENCFF447KSW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF447KSW/@@download/ENCFF447KSW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 control rep1 read2 ENCFF111AWS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF111AWS/@@download/ENCFF111AWS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 control rep2 read1 ENCFF497HLJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF497HLJ/@@download/ENCFF497HLJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SART3_K562"
out="$BASE_DIR/RBP_knockdown/SART3_K562/SART3_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SART3_K562 control rep2 read2 ENCFF561NSL"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF561NSL/@@download/ENCFF561NSL.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 KO rep1 read1 ENCFF541HLQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF541HLQ/@@download/ENCFF541HLQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 KO rep1 read2 ENCFF855NHU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF855NHU/@@download/ENCFF855NHU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 KO rep2 read1 ENCFF825DLG"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF825DLG/@@download/ENCFF825DLG.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 KO rep2 read2 ENCFF823ZLQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF823ZLQ/@@download/ENCFF823ZLQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 control rep1 read1 ENCFF025YLM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF025YLM/@@download/ENCFF025YLM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 control rep1 read2 ENCFF697WWV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF697WWV/@@download/ENCFF697WWV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 control rep2 read1 ENCFF317AWM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF317AWM/@@download/ENCFF317AWM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/SF3B4_HepG2"
out="$BASE_DIR/RBP_knockdown/SF3B4_HepG2/SF3B4_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] SF3B4_HepG2 control rep2 read2 ENCFF023MFT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF023MFT/@@download/ENCFF023MFT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 KO rep1 read1 ENCFF682WVW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF682WVW/@@download/ENCFF682WVW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 KO rep1 read2 ENCFF637BLZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF637BLZ/@@download/ENCFF637BLZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 KO rep2 read1 ENCFF306FRF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF306FRF/@@download/ENCFF306FRF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 KO rep2 read2 ENCFF424BJP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF424BJP/@@download/ENCFF424BJP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 control rep1 read1 ENCFF427IYE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF427IYE/@@download/ENCFF427IYE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 control rep1 read2 ENCFF554VFV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF554VFV/@@download/ENCFF554VFV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 control rep2 read1 ENCFF032JQZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF032JQZ/@@download/ENCFF032JQZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TARDBP_HepG2"
out="$BASE_DIR/RBP_knockdown/TARDBP_HepG2/TARDBP_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TARDBP_HepG2 control rep2 read2 ENCFF191JJU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF191JJU/@@download/ENCFF191JJU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 KO rep1 read1 ENCFF228TQK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF228TQK/@@download/ENCFF228TQK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 KO rep1 read2 ENCFF773CAF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF773CAF/@@download/ENCFF773CAF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 KO rep2 read1 ENCFF647VRD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF647VRD/@@download/ENCFF647VRD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 KO rep2 read2 ENCFF845KED"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF845KED/@@download/ENCFF845KED.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 control rep1 read1 ENCFF726LTF"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF726LTF/@@download/ENCFF726LTF.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 control rep1 read2 ENCFF569YVH"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF569YVH/@@download/ENCFF569YVH.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 control rep2 read1 ENCFF891EGO"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF891EGO/@@download/ENCFF891EGO.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/TIA1_K562"
out="$BASE_DIR/RBP_knockdown/TIA1_K562/TIA1_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] TIA1_K562 control rep2 read2 ENCFF667EXM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF667EXM/@@download/ENCFF667EXM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 KO rep1 read1 ENCFF020XNK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF020XNK/@@download/ENCFF020XNK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 KO rep1 read2 ENCFF354AMD"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF354AMD/@@download/ENCFF354AMD.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 KO rep2 read1 ENCFF298TSM"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF298TSM/@@download/ENCFF298TSM.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 KO rep2 read2 ENCFF229BQW"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF229BQW/@@download/ENCFF229BQW.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 control rep1 read1 ENCFF291QQH"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF291QQH/@@download/ENCFF291QQH.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 control rep1 read2 ENCFF602GIQ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF602GIQ/@@download/ENCFF602GIQ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 control rep2 read1 ENCFF503VRZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF503VRZ/@@download/ENCFF503VRZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/U2AF2_HepG2"
out="$BASE_DIR/RBP_knockdown/U2AF2_HepG2/U2AF2_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] U2AF2_HepG2 control rep2 read2 ENCFF105YHI"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF105YHI/@@download/ENCFF105YHI.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 KO rep1 read1 ENCFF630ZDV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF630ZDV/@@download/ENCFF630ZDV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 KO rep1 read2 ENCFF993TUN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF993TUN/@@download/ENCFF993TUN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 KO rep2 read1 ENCFF064IDI"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF064IDI/@@download/ENCFF064IDI.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 KO rep2 read2 ENCFF529LIT"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF529LIT/@@download/ENCFF529LIT.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 control rep1 read1 ENCFF361RLP"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF361RLP/@@download/ENCFF361RLP.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 control rep1 read2 ENCFF043VJU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF043VJU/@@download/ENCFF043VJU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 control rep2 read1 ENCFF803FSB"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF803FSB/@@download/ENCFF803FSB.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPL_K562"
out="$BASE_DIR/RBP_knockdown/HNRNPL_K562/HNRNPL_K562_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPL_K562 control rep2 read2 ENCFF827KTS"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF827KTS/@@download/ENCFF827KTS.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 KO rep1 read1 ENCFF370WAJ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF370WAJ/@@download/ENCFF370WAJ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 KO rep1 read2 ENCFF841CWK"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF841CWK/@@download/ENCFF841CWK.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 KO rep2 read1 ENCFF026VNR"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF026VNR/@@download/ENCFF026VNR.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 KO rep2 read2 ENCFF443IPN"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF443IPN/@@download/ENCFF443IPN.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_control1_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 control rep1 read1 ENCFF427IYE"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF427IYE/@@download/ENCFF427IYE.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_control1_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 control rep1 read2 ENCFF554VFV"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF554VFV/@@download/ENCFF554VFV.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_control2_1.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 control rep2 read1 ENCFF032JQZ"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF032JQZ/@@download/ENCFF032JQZ.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi

mkdir -p "$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2"
out="$BASE_DIR/RBP_knockdown/HNRNPLL_HepG2/HNRNPLL_HepG2_control2_2.fastq.gz"
tmp="${out}.part"
if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then
  echo "[SKIP] already exists: $out"
else
  echo "[GET] HNRNPLL_HepG2 control rep2 read2 ENCFF191JJU"
  wget -c -O "$tmp" https://www.encodeproject.org/files/ENCFF191JJU/@@download/ENCFF191JJU.fastq.gz
  gzip -t "$tmp"
  mv "$tmp" "$out"
fi


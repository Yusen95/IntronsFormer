import sys


# 0-based column indices.
FPKM_GENE_ID_COL = 3  # gene_id column in Cufflinks genes.fpkm_tracking
FPKM_VALUE_COL = 9  # FPKM column in Cufflinks genes.fpkm_tracking

IRF_NAME_COL = 3  # IRFinder composite name column
IRRATIO_COL = 19  # IRratio
INTRON_DEPTH_COL = 8  # IntronDepth


def main(fpkm_path, irfinder_path, output_ir_bed, output_nonir_bed):
    fpkm_dict = {}
    with open(fpkm_path, "r") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(FPKM_GENE_ID_COL, FPKM_VALUE_COL):
                continue

            gene_id = parts[FPKM_GENE_ID_COL].split(".")[0]
            try:
                fpkm_dict[gene_id] = float(parts[FPKM_VALUE_COL])
            except ValueError:
                continue

    with open(irfinder_path, "r") as infile, \
            open(output_ir_bed, "w") as ir_out, \
            open(output_nonir_bed, "w") as nonir_out:
        next(infile)

        for line in infile:
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= max(IRF_NAME_COL, IRRATIO_COL, INTRON_DEPTH_COL):
                continue

            name_parts = cols[IRF_NAME_COL].split("/")
            if len(name_parts) < 2:
                continue

            ensembl_id = name_parts[1].split(".")[0]

            try:
                irratio = float(cols[IRRATIO_COL])
                intron_depth = int(float(cols[INTRON_DEPTH_COL]))
            except ValueError:
                continue

            bed_entry = "\t".join(cols[:6]) + "\n"

            is_retained = irratio >= 0.1 and intron_depth >= 10
            is_non_retained = irratio <= 0.01 and intron_depth < 10

            if fpkm_dict.get(ensembl_id, 0) < 1:
                continue

            if is_retained:
                ir_out.write(bed_entry)
            elif is_non_retained:
                nonir_out.write(bed_entry)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python scripts/01_filter_ir_events.py "
            "<fpkm.txt> <irfinder.txt> <IRs.bed> <nonIRs.bed>"
        )
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

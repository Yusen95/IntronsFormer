# Paper Reproducibility Repository

This repository contains metadata, example preprocessing outputs, processed inputs, and downstream analysis scripts for reproducing the analyses in the paper.

The repository is organized as a reproducibility workflow rather than a standalone software package. Standard preprocessing tools such as IRFinder and Cufflinks are documented, and example outputs are provided so downstream scripts can be tested without re-running all raw-data processing steps.

## Workflow Overview

1. Collect ENCODE RNA-seq datasets for selected human cell lines.
2. Quantify intron retention with IRFinder.
3. Quantify gene expression as FPKM with Cufflinks.
4. Build processed intron retention and expression matrices.
5. Run downstream analyses used in the paper.

## Reference Setup

- Genome build: hg38
- Annotation: Ensembl release 111 for hg38
- Intron retention tool: IRFinder
- Expression quantification tool: Cufflinks

## Repository Layout

```text
metadata/
  rnaseq_sources.tsv          # ENCODE RNA-seq sources used for IRFinder/Cufflinks

example/
  irfinder/                   # Example IRFinder output
  cufflinks/                  # Example Cufflinks FPKM output

data/
  processed/                  # Processed matrices used by downstream scripts

scripts/
  01_*.py or 01_*.R           # Downstream analysis scripts, added as the workflow is built
```

## Current Entry Point

Downstream analyses are intended to start from processed IRFinder and FPKM result tables. The complete raw FASTQ/BAM processing workflow is not included because IRFinder and Cufflinks are used as standard tools without custom algorithmic changes.

An example IRFinder result and an example Cufflinks result should be placed under `example/` so users can validate the downstream code path.

## Metadata To Complete

The following fields should be completed before release:

- ENCODE RNA-seq accessions for all cell lines
- IRFinder version
- Cufflinks version
- Exact Ensembl 111 GTF file name
- Example IRFinder output file name
- Example Cufflinks output file name
- Rules for merging or averaging replicates

## License

This repository is released under the MIT License.

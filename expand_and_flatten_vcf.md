# Expand and Flatten VCF
The [canonical format for a VCF file](https://samtools.github.io/hts-specs/VCFv4.2.pdf) contains 8 "fixed fields"

`#CHROM POS ID  REF ALT QUAL  FILTER  INFO`

The `INFO` column contains key-value pairs separated by a delimiter `;`.

**Example from ClinVar:**
```
ALLELEID=959428;CLNDISDB=MedGen:CN517202;CLNDN=not_provided;CLNHGVS=NC_000001.11:g.943363G>C;CLNREVSTAT=criteria_provided,_single_submitter;CLNSIG=Uncertain_significance;CLNVC=single_nucleotide_variant;CLNVCSO=SO:0001483;GENEINFO=SAMD11:148398;MC=SO:0001583|missense_variant;ORIGIN=1
```

**Example from Kaviar:**
```
AF=0.0000379,0.0000379;AC=1,1;AN=26378;END=10145
```

Also, when multiple variants are called for a single genomic coordinate, these variants are 

# Generate kaviar VCF Schema from Header


The _kaviar.vcf_ file has a column called `INFO` that has key-value pairs for auxiliary information about each variant. For example:

```
ALLELEID=959428;CLNDISDB=MedGen:CN517202;CLNDN=not_provided;CLNHGVS=NC_000001.11:g.943363G>C;CLNREVSTAT=criteria_provided,_single_submitter;CLNSIG=Uncertain_significance;CLNVC=single_nucleotide_variant;CLNVCSO=SO:0001483;GENEINFO=SAMD11:148398;MC=SO:0001583|missense_variant;ORIGIN=1
```

The header contains schema for the keys given in lines such as:

```
##INFO=<ID=AF_ESP,Number=1,Type=Float,Description="allele frequencies from GO-ESP">
##INFO=<ID=AF_EXAC,Number=1,Type=Float,Description="allele frequencies from ExAC">
##INFO=<ID=AF_TGP,Number=1,Type=Float,Description="allele frequencies from TGP">
```

However, these schema lines do not include the other columns (not `INFO`), which are

`CHROM`, `POS`, `ID`, `REF`, `ALT`, `QUAL`, `FILTER`

I created the schema for these "by hand"

To build the appropriate schema for uploading to BigQuery, I:
1. Defined the base schema by hand
1. Parsed the schema from the VCF file
1. Renamed the parsed schema
1. Added the parsed schema to the base schema


## Hand-Made JSON schema for base fields (not INFO) in kaviar.vcf

```{python active="", eval=FALSE}
##fileformat=VCFv4.1
##fileDate=20160209
##source=bin/makeVCF.pl
##reference=file:///proj/famgen/resources/Kaviar-160204-Public/bin/../tabixedRef/hg19.gz
##version=Kaviar-160204 (hg19)
##kaviar_url=http://db.systemsbiology.org/kaviar
##publication=Glusman G, Caballero J, Mauldin DE, Hood L and Roach J (2011) KAVIAR: an accessible system for testing SNV novelty. Bioinformatics, doi: 10.1093/bioinformatics/btr540
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele Count">
##INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in data sources">
##INFO=<ID=END,Number=.,Type=Integer,Description="End position">
##INFO=<ID=DS,Number=A,Type=String,Description="Data Sources containing allele">
```

```{python}
base_kaviar_variant_schema = \
[
  {
    "description": "Chromosome",
    "mode": "NULLABLE",
    "name": "CHROM",
    "type": "STRING"
  },
  {
    "description": "Start position (0-based). Corresponds to the first base of the string of reference bases.",
    "mode": "NULLABLE",
    "name": "POS",
    "type": "INTEGER"
  },
  {
    "description": "",
    "mode": "NULLABLE",
    "name": "ID",
    "type": "STRING"
  },
  {
    "description": "Reference bases.",
    "mode": "NULLABLE",
    "name": "REF",
    "type": "STRING"
  },
  {
    "description": "Alternate bases.",
    "mode": "NULLABLE",
    "name": "ALT",
    "type": "STRING"
  },
  {
    "description": "Phred-scaled quality score (-10log10 prob(call is wrong)). Higher values imply better quality.",
    "mode": "NULLABLE",
    "name": "QUAL",
    "type": "STRING"
  },
  {
    "description": "List of failed filters (if any) or \"PASS\" indicating the variant has passed all filters.",
    "mode": "NULLABLE",
    "name": "FILTER",
    "type": "STRING"
  }
]
```
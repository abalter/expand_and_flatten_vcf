# Expand and Flatten VCF
`./expand_and_flatten_vcf.py -i kaviar_100.vcf -o kaviar_expanded.vcf`

## VCF Format
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
Also, when multiple variants are called for a single genomic coordinate, these variants are included in a single row for that coordinate are comma-delimited in that column. Associated data for these variants that might be in the `INFO` column, such as allele frequency (`AF`) are then also comma delimited. For example, the following row from Kaviar identifies three possible variants, and three associated values for the allele frequency and allele count (`AC`):
```
1	10108	.	C	CA,CCT,CT	.	.	AF=0.0000379,0.0018197,0.0003033;AC=1,48,8;AN=26378
```
In this case, the values for addional data 

## VCF Header
The VCF header lines specify the schema for the data contained in the `INFO` column.

**Full Kaviar header:**
```
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

**Samples from ClinVar header:**
```
##INFO=<ID=CLNDN,Number=.,Type=String,Description="ClinVar's preferred disease name for the concept specified by disease identifiers in CLNDISDB">
##INFO=<ID=CLNDNINCL,Number=.,Type=String,Description="For included Variant : ClinVar's preferred disease name for the concept specified by disease identifiers in CLNDISDB">
##INFO=<ID=CLNDISDB,Number=.,Type=String,Description="Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN">
##INFO=<ID=CLNDISDBINCL,Number=.,Type=String,Description="For included Variant: Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN">
##INFO=<ID=CLNHGVS,Number=.,Type=String,Description="Top-level (primary assembly, alt, or patch) HGVS expression.">
##INFO=<ID=CLNREVSTAT,Number=.,Type=String,Description="ClinVar review status for the Variation ID">
##INFO=<ID=CLNSIG,Number=.,Type=String,Description="Clinical significance for this single variant">
```
 
## Generate Full VCF Schema from Header
While there are many standard or customary INFO fields, such as those in the documentation, custom ones are fine, as in the ClinVar example. In order to generate a full schema specification we need to parse the header rows. We combine this parsed schema with the schema for the fixed fields (constructed by hand), which is shown below.

## Usage
```
usage: expand_and_flatten_vcf.py [-h] --input_vcf INPUT_VCF [--output_vcf OUTPUT_VCF] [--info_column_index INFO_COLUMN_INDEX]
                                 [--info_delimiter INFO_DELIMITER] [--base_schema BASE_SCHEMA]

Expand INFO column in VCF Files and ouput or write.

VCF Files have a column called INFO with 'key=vlaue' 
pairs separated by ';'. 

For example:

<example of INFO column>

Also, when multiple variants are called for a single 
genomic position, these alternates are comma-separated
in the VCF file. In these situations, the genomic position 
is repeated with the alternate variants in successive rows. 
For example:

<example of multiple variants and expanded version> 

optional arguments:
  -h, --help            show this help message and exit
  --input_vcf INPUT_VCF, -i INPUT_VCF
                        Input VCF file with INFO column as string with key-value pairs.
  --output_vcf OUTPUT_VCF, -o OUTPUT_VCF
                        Expanded VCF file
  --info_column_index INFO_COLUMN_INDEX, -x INFO_COLUMN_INDEX
                         0-indexed index of the INFO column. Default value, 
                         according to spec, is 7.
                         
  --info_delimiter INFO_DELIMITER, -d INFO_DELIMITER
                         Custom separator for INFO key-value pairs in case of some 
                         weird file. Default value, according to standard, is ";"
                         
  --base_schema BASE_SCHEMA, -b BASE_SCHEMA
                        The standard VCF format has 7 columns of data and the INFO column. 
                        The schema for these first 7 "base" columns are not in the header. 
                        This should be a JSON string containing the base schema if different 
                        than the default ones in this package.
```

## Schema for Fixed Fields
```
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
    "type": "FLOAT"
  },
  {
    "description": "List of failed filters (if any) or \"PASS\" indicating the variant has passed all filters.",
    "mode": "NULLABLE",
    "name": "FILTER",
    "type": "STRING"
  }
]
```
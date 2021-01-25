#!/usr/bin/env python

import os
import re
import sys
import json
import textwrap

fixed_schema = [
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
    "description": "dbSNP ID (rs###)",
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


class VCF_INFO_EXPANDER():

    fixed_schema = [
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
        "description": "dbSNP ID (rs###)",
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
    
    def __init__(
            self,
            input_vcf_file="",
            output_vcf_file=None,
            info_column_index=7,
            info_delimiter = ";",
            fixed_schema=fixed_schema
        ):
        
#         print("__init__")
        
        self.input_vcf_file = input_vcf_file
        self.output_vcf_file = output_vcf_file
        self.info_column_index = info_column_index
        self.fixed_schema = json.loads(fixed_schema)
#         print(self.fixed_schema)
        self.info_delimiter = info_delimiter
        
        self.info_schema = self.parseVCF_Schema()
#         print(self.info_schema)
        
        self.full_schema = self.fixed_schema + self.info_schema
        
        self.base_fields = [var["name"] for var in self.fixed_schema]
        self.info_fields = [var["name"] for var in self.info_schema]
        self.all_fields = self.base_fields + self.info_fields
        
#         print(self.info_schema)
        
    def parseVCF_Schema(self):
#         print("parseVCF_Schema")
                
        vcf_file = self.input_vcf_file
        info_column_index = self.info_column_index
        
        info_schema = []
        
        with open(vcf_file) as vcf:

            for line in vcf:

                ### Capture lines that have field info
                ### They look like with "##INFO=<k=v,k=v, ...>"
                if bool(re.search("^##INFO", line)):
                    info_data = re.sub("^##INFO=<(.*)>", r"\1", line).strip()
                    ### regex to split by commas, but only outside of quotes
                    regex = r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"
                    kv_pairs = re.split(regex, info_data)
                    info_dict = dict(item.split("=") for item in kv_pairs)

                    ### Rename necessary fields to match
                    ### BigQuery schema fields
                    ### Description --> description
                    ### Type --> type
                    ### ID --> name
                    ### Number --> .=Nullable, 1=Repeatable
                    info_dict['description'] = info_dict['Description']
                    del info_dict['Description']
                    info_dict['type'] = info_dict['Type']
                    del info_dict['Type']
                    info_dict['name'] = info_dict['ID']
                    del info_dict['ID']
                    if info_dict['Number'] == '.':
                        info_dict['mode'] = 'NULLABLE'
                    else:
                        info_dict['mode'] = 'NULLABLE'
                    del info_dict['Number']

                    ### Add parsed schema to base schema
                    info_schema.append(info_dict )

                ### ignore lines that are header lines but not field info
                elif bool(re.search("^##", line)):
                    pass

                ### done with header, stop reading. Prevents reading through
                ### entire file.
                else:
                    break

        return info_schema

    
    def getNumHeaderLines(self):
#         print("getNumHeaderLines")
        
        filename = self.input_vcf_file
        num_header_lines = 0
        
        with open(filename) as vcf:
            for line in vcf:

                ### capture lines that have field info
                if bool(re.search("^##", line)):
        #             print(line)
                    num_header_lines += 1

                ### done with header, stop reading
                else:
                    break
        return num_header_lines

    
    def expandInfoData(self, info):
#         print("expandInfoData")
        
        fields = self.info_fields
        
        kv_pairs = [pair.split("=") for pair in info.split(";")]
        info_dict = {kv[0]:kv[1] for kv in kv_pairs}

        if not fields:
            fields = info_dict.keys()

        info_dict = {k:info_dict.get(k, ".").split(",") for k in fields}

        return info_dict


    def splitRowDict(
            self, 
            row_dict, 
            alt_sep=",", 
            alt_field="ALT"
        ):
#         print("splitRowDict")
        
        num_alts = len(row_dict[alt_field])

        row_dicts = [{}]*num_alts
        for i in range(num_alts):
            row_dicts[i] = {k:v[ min(i, len(v)-1) ] for k,v in row_dict.items()}

        return row_dicts


    def convertRowStringToRowDict(
            self, 
            row_string
        ):
#         print("convertRowStringToRowDict")
        
        info_column_index = self.info_column_index
        info_delimiter = self.info_delimiter
        info_fields = self.info_fields
        base_fields = self.base_fields

        values = row_string.strip().split("\t")
        info_data = values.pop(info_column_index)

        row_dict = self.expandInfoData(info_data)
        for i in range(len(base_fields)):
            row_dict[base_fields[i]] = values[i].split(",")

        return row_dict


    def writeRowDict(self,row_dict):

        fields = self.all_fields 
        row_string = "\t".join([row_dict[field] for field in fields]) + "\n"
        self.outfile.write(row_string)


    def expandAndFlatten(self):

#         print("expandAndFlatten")
        
        info_column_index = self.info_column_index
        info_schema = self.info_schema
        fixed_schema = self.fixed_schema
        infilename = self.input_vcf_file
        outfilename = self.output_vcf_file
        
        base_fields = self.base_fields
        info_fields = self.info_fields
        all_fields = self.all_fields

        if outfilename is None:
            self.outfile = sys.stdout
        else:
            self.outfile = open(outfilename, "w")
        
        ### Write header
        dummy = self.outfile.write("\t".join(all_fields) + "\n")

        num_header_lines = self.getNumHeaderLines()

        with open(infilename) as file:
            ### Skip header
            for _ in range(num_header_lines+1):
                dummy = next(file)

            ### Start reading
            for line in file:
#                 print(line)
                row_dict = self.convertRowStringToRowDict(row_string=line)
                row_dicts = self.splitRowDict(row_dict)

                for row_dict in row_dicts:
                    self.writeRowDict(row_dict)

        dummy = self.outfile.close()
        
        
    def getSchema(self):
#         print("getSchema")
        
        if self.output_vcf_file is None:
            self.outfile = sys.stdout
        else:
            self.outfile = open(self.output_vcf_file, "w")
            
        dummy = self.outfile.write(json.dumps(self.full_schema, indent=2))


if __name__ == "__main__":
        
    import argparse

    parser = argparse.ArgumentParser(
        description = """\
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
""",
        formatter_class=argparse.RawTextHelpFormatter
        )
    
    parser.add_argument('operation',
        type = str,
        help = """\
 Which operation to perform. To export an expanded and flattend
 vcf file, use "vcf". To export the full schema use "schema". The
 default value is "vcf" if not specified.
 """,
        choices = ["vcf", "schema"],
        default = "vcf"
        )
    
    parser.add_argument('--input_vcf', '-i',
        required=True,
        type=str,
        help="Input VCF file with INFO column as string with key-value pairs.",
        default = None
        )
    parser.add_argument('--output_vcf', '-o',
        required=False,
        type=str,
        help="Expanded VCF file",
        default=None
        )
    parser.add_argument('--info_column_index', '-x',
        required=False,
        type=int,
        help="""\
 0-indexed index of the INFO column. Default value, 
 according to spec, is 7.
 """,
        default = 7
        )
    parser.add_argument('--info_delimiter', '-d',
        required=False,
        type=str,
        help="""\
 Custom separator for INFO key-value pairs in case of some 
 weird file. Default value, according to standard, is \";\"
 """,
        default=";"
        )
    parser.add_argument('--fixed_schema', '-b',
        required=False,
        type=str,
        help="""\
The standard VCF format has 7 columns of data and the INFO column. 
The schema for these first 7 \"base\" columns are not in the header. 
This should be a JSON string containing the base schema if different 
than the default ones in this package. 
Check `VCF_INFO_EXPANDER.fixed_schema`
""",
        default=json.dumps(fixed_schema)
        )

    args = parser.parse_args()
    
    operation = args.operation
    print("operation", operation)
    input_vcf_file = args.input_vcf
#     print("input_vcf_file", input_vcf_file)
    output_vcf_file = args.output_vcf
#     print("output_vcf_file", output_vcf_file)
    info_delimiter = args.info_delimiter
#     print("info_delimiter", info_delimiter)
    info_column_index = args.info_column_index
#     print("info_column_index", info_column_index)
    fixed_schema = args.fixed_schema
    if fixed_schema is None:
        fixed_schema = json.dumps(fixed_schema)
#     print("fixed_schema", fixed_schema)
                        
                        
    expander = VCF_INFO_EXPANDER(
        input_vcf_file=input_vcf_file,
        output_vcf_file=output_vcf_file,
        info_column_index=info_column_index,
        info_delimiter=info_delimiter,
        fixed_schema=fixed_schema
    )

    if operation == "vcf":
        expander.expandAndFlatten()
    else:
        expander.getSchema()
        
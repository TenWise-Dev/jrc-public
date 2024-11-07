#!/usr/bin/env python

'''
This script is used to filter a JSON file based on open access status and save the filtered data to a tab-delimited txt file.
The script has two required arguments. ::

    Required:
    
    -j : The path to the PMID JSON file
    -o : The path to the output tab-delimited txt file
    
    Usage:
    
    python3 Database2PDF.py -j database_file -o output_file
    
'''

import ijson
import argparse
from tqdm import tqdm

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the PMID JSON file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the path to the output tab-delimited txt file")

    # Read arguments from the command line
    args = parser.parse_args()
    
    output_dict = {}
    
    # Stream over the JSON file
    with open(args.json_file, 'rb') as file:
        # Create a parser object over the JSON file
        parser = ijson.items(file, 'item')
        
        # Iterate over the JSON objects
        for item in tqdm(parser):
            if 'is_oa' in item and 'pdf_url' in item:
                if item['is_oa'] and item['pdf_url'] != "NA":
                    output_dict[item['pmid']] = item['pdf_url']
                    
    # Write the filtered data to a tab-delimited txt file
    with open(args.output_file, 'w') as file:
        for key, value in output_dict.items():
            file.write(key + '\t' + value + '\n')
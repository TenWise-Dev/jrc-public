#!/usr/bin/env python

'''
This script is used to convert an Excel file to a JSON file using the PMID column as the key.
The resulting JSON file can then be used to update the database.
The script has two required arguments. ::

    Required:
    
    -e : The path to the XLSX file
    -j : The path to the output JSON file
    
    Usage:
    
    python3 Excel2JSON.py -e ../example/demo_excel.xlsx -j ../YOUR_FOLDER/update_file.json
    
'''

import argparse
import pandas as pd
import json
from tqdm import tqdm

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-e", dest="excel_file", required=True, help="Provide the path to the Excel file")
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the Output JSON file")

    # Read arguments from the command line
    args=parser.parse_args()
    
    print(f"Converting {args.excel_file} to {args.json_file}")
    
    # Read the Excel file
    df = pd.read_excel(args.excel_file)
    
    # Convert the DataFrame to a dictionary
    result_json = df.set_index("pmid").T.to_dict("dict")
    
    print(f"Total records: {len(result_json)}")
    
    print("Removing NaN values")    
    # Remove NaN values from the dictionary
    for key, value in tqdm(result_json.items()):
        result_json[key] = {k: v for k, v in value.items() if pd.notna(v)}
    
    print("Finished, saving the JSON file")
    # Save the dictionary to a JSON file
    with open(args.json_file, 'w') as file:
        json.dump(result_json, file, indent=4)
    
    
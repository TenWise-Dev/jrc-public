#!/usr/bin/env python

'''
This script is used to update the PMID JSON file with additional information from a tab-delimited txt file.
The script has three required arguments. ::

    Required:
    
    -j : The path to the PMID JSON file
    -t : The path to the tab-delimited triplets txt file
    -o : The name of the output file
    
    Usage:
    
    python3 DatabaseUpdate.py -j database_file -t triplets_file -o output_file
    
'''

# Import the required libraries
import json
import argparse
import pandas as pd
import ijson

def update_json_from_triplets(json_file: str, triplet_file: str, output_file: str) -> None:
    
    # Make docstring with rst syntax
    """
    Update the JSON file with the information from the triplets file. Save it back to the JSON file.\n
    \n
    Parameters:\n
    - json_file: The path to the PMID JSON file\n
    - triplet_file: The path to the tab-delimited triplets txt file\n
    - output_file: The name of the output file
    \n
    Returns:\n
    - None
    """
    
    # Check if output file exists, if so, remove it
    try:
        with open(output_file, 'r') as file:
            pass
        with open(output_file, 'w') as file:
            pass
    except FileNotFoundError:
        with open(output_file, 'w') as file:
            pass    
            
    # First create update df
    update_df = pd.read_csv(triplet_file, sep='\t', header=None)
    update_df.columns = ['pmid', 'relation', 'value']
    
    # Change pmid to string
    update_df['pmid'] = update_df['pmid'].astype(str)
    
    # Convert the update data to a dictionary
    update_df = update_df.pivot(index='pmid', columns='relation', values='value').reset_index()
    update_df = update_df.fillna('')
    update_data = update_df.set_index('pmid').to_dict(orient='index')
    
    # Create an empty list to store the updated JSON objects
    output_list = []

    # Stream over the JSON file
    with open(json_file, 'rb') as file:
        # Create a parser object over the JSON file
        parser = ijson.items(file, 'item')
        
        # Iterate over the JSON objects
        for item in parser:
            # Check if the PMID is in the update data
            if item['pmid'] in update_data.keys():              
                # Get the index of the PMID in the update data
                # Update the JSON object with the new data
                item.update(update_data[item['pmid']])      
                # Add updated key to update data
                update_data.pop(item['pmid'])
            
            # Append the JSON object to the output list, whether it was updated or not
            output_list.append(item)

        # Append the remaining update data to the output list
        for key, value in update_data.items():
            # Add the PMID to the dictionary as first key
            value['pmid'] = key
            
            # Append the updated JSON object to the output list
            output_list.append(value)
        
        # Append the updated JSON object to the output file
        with open(output_file, 'a') as outfile:
            json.dump(output_list, outfile, indent=4)
    pass

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the PMID JSON file")
    parser.add_argument("-t", dest="triplets_file", required=True, help="Provide the path to the tab-delimited triplets txt file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output file")

    # Read arguments from the command line
    args=parser.parse_args()

    # Call the function
    update_json_from_triplets(json_file=args.json_file, triplet_file=args.triplets_file, output_file=args.output_file)

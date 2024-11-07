#!/usr/bin/env python

'''
This script is used to update the PMID JSON file with additional information from a tab-delimited txt file.
The script has two required arguments. ::

    Required:
    
    -j : The path to the PMID JSON file
    -t : The path to the tab-delimited triplets txt file
    
    Usage:
    
    python3 DatabaseUpdate.py -j database_file -t triplets_file
    
'''

# Import the required libraries
import json
import argparse

def update_json_from_triplets(json_file: str, triplet_file: str) -> None:
    # Make docstring with rst syntax
    """
    Update the JSON file with the information from the triplets file. Save it back to the JSON file.\n
    \n
    Parameters:\n
    - json_file: The path to the PMID JSON file\n
    - triplet_file: The path to the tab-delimited triplets txt file\n
    \n
    Returns:\n
    - None
    """
    
    # Read the existing JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Process each triplet from the tab-delimited file
    with open(triplet_file, 'r') as file:
        for line in file:
            subject, relation, object_ = line.strip().split('\t')
            if subject in data.keys():
                data[subject][relation] = object_      

    # Write the updated data back to the JSON file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the PMID JSON file")
    parser.add_argument("-t", dest="triplets_file", required=True, help="Provide the path to the tab-delimited triplets txt file")

    # Read arguments from the command line
    args=parser.parse_args()

    # Call the function
    update_json_from_triplets(json_file=args.json_file, triplet_file=args.triplets_file)

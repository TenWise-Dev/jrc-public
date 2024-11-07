#!/usr/bin/env python

'''
This script is used to retrieve PMIDs from a data folder with csv files in a specific format (JRC Project).
The script has two required arguments. ::

    Required:
    
    -d : The path to the datafolder
    -o : The name of the output file
    
    Usage:
    
    python3 pmid_extraction.py -d datafolder -o output_file
    
'''

# Import the required libraries
import os
import pandas as pd
import argparse

def get_pmids(datafolder: str, output_file: str) -> None:
    
    """
    Get all the PMIDs from the datafolder and save them to a text file.\n
    \n
    Parameters:\n
    - datafolder: The path to the datafolder\n
    - output_file: The name of the output file\n
    \n
    Returns:\n
    - None
    """
    
    # Make a large list to store the data
    pmids = list()

    for filename in os.listdir(datafolder):
        if not filename.endswith('.csv'):
            continue
        # Get the path to the datafile
        datafile_path = os.path.join(datafolder, filename)
        
        # Open the datafile
        data = pd.read_csv(datafile_path)
        
        # Filter id column on values containing "PMID"
        data = data[data['id'].str.contains('PMID')]
        
        new_entries = data['id'].str.split(':').str[1].values
        
        # Check if the entry is already in the dictionary, else add it
        for entry in new_entries:
            if entry not in pmids:
                pmids.append(entry)

    # Get the path to the output file
    output_file = os.path.join(datafolder, output_file)
        
    # Save data to separate lines in a text file
    with open(output_file, 'w') as f:
        for item in pmids:
            f.write("%s\n" % item)
            

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", dest="datafolder", required=True, help="Provide the path to the datafolder")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output file")

    # Read arguments from the command line
    args=parser.parse_args()

    # Call the function
    get_pmids(datafolder=args.datafolder, output_file=args.output_file)
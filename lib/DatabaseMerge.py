#!/usr/bin/env python

'''
This script is used to update the PMID JSON file with additional information from a tab-delimited txt file.
The script has three required arguments. ::

    Required:
    
    -j : The path to the current JSON file
    -u : The path to the file with additional information
    -o : The name of the output JSON file
    
    Usage:
    
    python3 DatabaseMerge.py -j ../example/demo_database.json -u ../example/tagged_abstracts.json -o ../YOUR_FOLDER/demo_database_merge.json
    
'''

# Import the required libraries
import ijson
import json
import argparse

def database_merge(json_file: str, update_file: str, output_file: str) -> None:
    # Make docstring with rst syntax
    """
    Update the main database JSON file with the information from another update JSON file. Save it back to a new updated database JSON file.\n
    The main database JSON file is expected to have the structure:\n
    \n
    .. code-block:: json
    
        [
            {
                "pmid": "PMID1",
                "doi": "DOI1",
                "title": "TITLE1"
            },
            {
                "pmid": "PMID2",
                "doi": "DOI2",
                "title": "TITLE2"
            }
        ]
    \n
    Update JSON files are expected to have the structure:\n
    \n
    .. code-block:: json
    
        {
            "PMID1": {
                "author": "AUTHOR1",
                "abstract": "ABSTRACT1"
                },
            "PMID2": {
                "author": "AUTHOR2",
                "abstract": "ABSTRACT2"
                }
        }
    \n
    Parameters:\n
    - json_file: The path to the current JSON file\n
    - update_file: The path to the file with additional information\n
    - output_file: The name of the output JSON file
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
    
    # Load the update json file
    with open(update_file, 'r') as file:
        update_data = json.load(file)
            
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
                
                
    

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the PMID JSON file")
    parser.add_argument("-u", dest="update_file", required=True, help="Provide the path to the update dict file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output file")

    # Read arguments from the command line
    args=parser.parse_args()

    # Call the function
    database_merge(json_file=args.json_file, update_file=args.update_file, output_file=args.output_file)

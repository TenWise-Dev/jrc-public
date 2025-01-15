#!/usr/bin/env python

'''
This script is used to load the records from the JSON database and tag the abstracts with a set of keywords
The script has three required arguments. ::

    Required:
    
    -j : The path to the json database
    -k : The path to keyword file
    -o : The path to the output file
    
    
    Usage:
    
    python3 PMID2Tags.py -j ../example/demo_pmids.json -k ../example/keyword_file.txt -o ../YOUR_FOLDER/tagged_abstracts.json 
       
    
'''

# Import the required libraries
import ijson
import argparse
import re
import json

def read_keyword_file(file_path: str) -> dict:
    # Make docstring with rst syntax
    """
    Read the keyword file and return the dictionary of categories and keywords.\n
    \n
    Parameters:\n
    - file_path: The path to the keyword file\n
    \n
    Returns:\n
    - category_dict: The dictionary of categories and keywords
    """
    
    category_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
                     
            # Split each line into category and instance
            category, instance = line.strip().split("\t")

            # Check if the category is already in the dictionary
            if category in category_dict:
                # If yes, append the instance to the existing list
                category_dict[category].append(instance)
            else:
                # If no, create a new list with the instance as the first element
                category_dict[category] = [instance]

    return category_dict


def process_text(text: str, category_dict: dict) -> dict:
    # Make docstring with rst syntax
    """
    Process the text and tag the abstracts with a set of keywords and return the results.\n
    \n
    Parameters:\n
    - text: The text to be processed\n
    - category_dict: The dictionary of categories and keywords\n
    \n
    Returns:\n
    - result_dict: The dictionary of categories and keywords with counts
    """
    
    result_dict = {}
    if text is None:
        return result_dict

    # Iterate over the categories and keywords
    for category, instances in category_dict.items():
        category_results = {}
        
        for instance in instances:
            # Create a regular expression string for the keyword
            re_string = instance

            # Add word boundaries to the regular expression
            re_string = "\\b" + re_string
   
            # Add optional 's' at the end of the keyword
            re_string = re_string+"s?"
            
            # Complete word boundary
            re_string = re_string + "\\b"
            
            # Add optional hyphens and spaces
            re_string = re.sub("[- ]","[- ]",re_string)

            # Find all matches of the keyword in the text
            matches = re.findall(re_string, text, flags=re.IGNORECASE)
            count = len(matches)
            if count == 0:
                continue
            category_results[instance] = count

        # Add results for the category to the main dictionary
        result_dict[category] = category_results

    return result_dict

if __name__ == "__main__":
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser()
    parser.add_argument("-j", dest = "json_file",    required = True,  help = "Provide the path to the datafolder")
    parser.add_argument("-o", dest = "output_file",  required = True,  help = "Provide the name of the output file")
    parser.add_argument("-k", dest = "keyword_file", required = True,  help = "Provide the name of the keyword_file")

    args=parser.parse_args()

    category_dict = read_keyword_file(args.keyword_file)
    #print(category_dict)
    with open(args.json_file, 'rb') as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'item')
        result = {}
        # Iterate over the JSON objects
        for item in parser:
        # Process each JSON object as needed
            result[item['pmid']] = {
                "tagging_scores": process_text(
                    text = f"{item['title']}\n{item['abstract']}", category_dict = category_dict
                    )
                }
           
    # Write the updated data back to a JSON file  
    with open(args.output_file, 'w') as file:
        json.dump(result, file, indent=4)        
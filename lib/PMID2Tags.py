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
    result_dict = {}
    if text is None:
        return result_dict

    for category, instances in category_dict.items():
        category_results = {}
        for instance in instances:
            re_string = instance

            re_string = "\\b" + re_string
   
            re_string = re_string+"s?"
            re_string = re_string + "\\b"
            re_string = re.sub("[- ]","[- ]",re_string)

            matches = re.findall(re_string, text, flags=re.IGNORECASE)
            count = len(matches)
            if count ==0:
                continue
            category_results[instance] = count

        # Add results for the category to the main dictionary
        result_dict[category] = category_results

    return result_dict

def print_results(myid, result_dict):
    for category, instances_dict in result_dict.items():
        
        for instance, count in instances_dict.items():
            print(f"{myid}\t{category}\t{instance}\t{count}")    



if __name__ == "__main__":
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser()
    parser.add_argument("-j", dest = "json_file",    required = True,  help = "Provide the path to the datafolder")
    parser.add_argument("-o", dest = "output_file",  required = True,  help = "Provide the name of the output file")
    parser.add_argument("-k", dest = "keyword_file", required = True,  help = "Provide the name of the keyword_file")

    args=parser.parse_args()

    category_dict = read_keyword_file(args.keyword_file)

    with open(args.json_file, 'rb') as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'item')
        result = {}
        # Iterate over the JSON objects
        for item in parser:
        # Process each JSON object as needed
            result[item['pmid']] = {"tagging_scores":process_text(text = item['abstract'], category_dict = category_dict)}
           
    # Write the updated data back to a JSON file  
    with open(args.output_file, 'w') as file:
        json.dump(result, file, indent=4)        
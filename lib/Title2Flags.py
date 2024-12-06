#!/usr/bin/env python

'''
This script is used to flag the title of the records with a set of negative keywords (if at least one keyword is found in the title, the pmid is flagged)
The script has three required arguments. ::

    Required:
    
    -j : The path to the json database
    -k : The path to keyword file
    -o : The path to the output file
    
    
    Usage:
    
    python3 Title2Flags.py -j ../example/demo_pmids.json -k ../example/negative_keyword_file.txt -o ../YOUR_FOLDER/tagged_abstracts.json 
       
    
'''

# Import the required libraries
import ijson
import argparse
import re
import json
from tqdm import tqdm

def read_keyword_file(file_path: str) -> list:
    keywords = []

    with open(file_path, 'r') as file:
        for line in file:
                     
            # Split each line into category and instance
            keyword = line.strip()

            # Check if keyword is already in the list
            if keyword not in keywords:
                keywords.append(keyword)
                
    return keywords


def process_text(text: str, keyword_list: list) -> dict:
    result_dict = {}
    if text is None:
        return result_dict

    for keyword in keyword_list:
        title_flag = 0
        
        re_string = keyword

        re_string = "\\b" + re_string

        re_string = re_string+"s?"
        re_string = re_string + "\\b"
        re_string = re.sub("[- ]","[- ]",re_string)

        matches = re.findall(re_string, text, flags=re.IGNORECASE)
        count = len(matches)
        if count != 0:
            title_flag = 1
            break

    return title_flag

if __name__ == "__main__":
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser()
    parser.add_argument("-j", dest = "json_file",    required = True,  help = "Provide the path to the datafolder")
    parser.add_argument("-o", dest = "output_file",  required = True,  help = "Provide the name of the output file")
    parser.add_argument("-k", dest = "keyword_file", required = True,  help = "Provide the name of the keyword_file")

    args=parser.parse_args()

    keyword_list = read_keyword_file(args.keyword_file)

    print("Starting to process the data...")

    with open(args.json_file, 'rb') as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'item')
        result = {}
        # Iterate over the JSON objects
        for item in tqdm(parser):
        # Process each JSON object as needed
            result[item['pmid']] = {"title_flag":process_text(text = item['title'], keyword_list = keyword_list)}
           
    print("Data processing completed...")
           
    # Write the updated data back to a JSON file  
    with open(args.output_file, 'w') as file:
        json.dump(result, file, indent=4)        
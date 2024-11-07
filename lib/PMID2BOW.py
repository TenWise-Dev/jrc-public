#!/usr/bin/env python

'''
This script is used to load the records from the JSON database and train a classifier to predict the categories using a set of keywords.
The script has three required arguments. ::

    Required:
    
    -j : The path to the json database
    -k : The path to keyword file
    -o : The path to the output file
    
    
    Usage:
    
    python3 PMID2BOW.py -j ../example/demo_pmids.json -k ../example/keyword_file.txt -o ../YOUR_FOLDER/demo_test_bow.npz
    
'''

# Import the required libraries
import ijson
import argparse
import re
import pandas as pd
import numpy as np

def read_keyword_file(file_path: str) -> dict:
    bow = []
    with open(file_path, 'r') as file:
        for line in file:
         # Split each line into category and instance
            category, instance = line.strip().split("\t")
            bow.append(instance)
    return bow


def process_text(text: str, bow: list) -> dict:
    result_dict = {}
  
    for instance in bow:
        # Adapt the regular expression as needed
  
        # Replace spaces and hyphens by hyphens or spaces
        regexp = re.sub("[- ]","[- ]", instance)
  
        if text is None:
            # In case we have no abstract!
            count=0
        if text:
            matches = re.findall(regexp, text, flags=re.IGNORECASE)
            count = len(matches)
        result_dict[instance] = count

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
    
    counter=0
    with open(args.json_file, 'rb') as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'item')
        result = {}
        # Iterate over the JSON objects
        for item in parser:
            counter = counter + 1
            result[item['pmid']] =process_text(text = item['abstract'], bow = category_dict)
  
    mypd = pd.DataFrame.from_dict(result).transpose() 
  
    np_pmids = np.array(list(result.keys()))
    np.savez_compressed(args.output_file, embeddings=mypd, keys=np_pmids)
    

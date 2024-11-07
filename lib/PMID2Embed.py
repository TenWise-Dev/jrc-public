#!/usr/bin/env python

'''
This script takes a set of PMIDs and retrieves the abstracts from the NCBI database.
These abstracts are then embedded using the SentenceTransformer model and saved to a Numpy file where the first column is the PMID and the rest of the columns are the embeddings.
The script has three required arguments. ::

    Required:
    
    -p: The path to the PMIDs file
    -d: The path to the database file
    -o: The name of the output file
    
    Usage:
    
    python3 PMID2Embed.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_test_embeddings.npz
    
'''

# Import the required libraries
import argparse
from datetime import datetime
import ijson
import numpy as np
from sentence_transformers import SentenceTransformer

def print_time(message: str) -> None:
    # Make docstring with rst syntax
    '''
    Print the current time and a message.\n
    \n
    Parameters:\n
    - message: The message to print\n
    '''
    
    print(f"{datetime.now().time().strftime('%H:%M:%S')} - {message}")

def load_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    # Make docstring with rst syntax
    '''
    Load the SentenceTransformer model.\n
    \n
    Parameters:\n
    - model_name: The name of the model to load\n
    \n
    Returns:\n
    - model: The SentenceTransformer model
    '''
    
    # Load the model
    model = SentenceTransformer(model_name)
    return model

def get_abstracts(pmids: list, database_file: str) -> dict:
    # Make docstring with rst syntax
    '''
    Get the abstracts from the JSON database file for a list of PMIDs.\n
    \n
    Parameters:\n
    - pmids: A list of PMIDs\n
    - database_file: The path to the JSON database file\n
    \n
    Returns:\n
    - pmid_abstracts: A dictionary with PMIDs as keys and abstracts as values
    - none_abstracts: The number of PMIDs with no abstracts
    '''
    
    pmid_abstracts = dict()
    none_abstracts = 0
    
    # Stream over the JSON file
    with open(database_file, 'rb') as file:
        # Create a parser object over the JSON file
        parser = ijson.items(file, 'item')
        
        # Iterate over the JSON objects
        for item in parser:
            if item['pmid'] in pmids and item['abstract'] is not None:
                pmid_abstracts[item['pmid']] = item['abstract']
            if item['abstract'] is None:
                none_abstracts += 1
    
    return pmid_abstracts, none_abstracts

def embed_abstracts(model, abstracts: dict) -> np.ndarray:
    # Make docstring with rst syntax
    '''
    Embed a dictionary of abstracts using the SentenceTransformer model.\n
    \n
    Parameters:\n
    - model: The SentenceTransformer model\n
    - abstracts: A dictionary with PMIDs as keys and abstracts as values\n
    \n
    Returns:\n
    - np_embedded: A numpy array with embeddings
    - np_pmids: A numpy array with PMIDs
    '''
    
    # Get the abstracts as a list
    abstract_list = list(abstracts.values())
    
    # Embed the abstracts with parallization
    np_embedded = model.encode(abstract_list, show_progress_bar=False)
    
    # Make np array with shape (123,) with PMIDs
    np_pmids = np.array(list(abstracts.keys()))
        
    return np_embedded, np_pmids

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pmid_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-d", dest="pmid_database", required=True, help="Provide the path to the datafolder")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output .npy file")

    # Read arguments from the command line
    args=parser.parse_args()

    # Read the PMIDs from the txt files
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
        
    print_time("Getting abstracts from the database...")    
        
    # Read the database JSON files
    pmid_abstracts, abs_none = get_abstracts(pmids=pmids, database_file=args.pmid_database)
    
    print_time(f"PMIDs with no abstracts: {abs_none}")

    print_time("Loading model...")
    
    model = load_model(model_name = 'all-MiniLM-L6-v2')
    
    print_time("Done loading model")
    print("-----------------------------")

    print_time("Embedding abstracts...")
    
    # Call the function
    np_embedded, np_pmids = embed_abstracts(model=model, abstracts=pmid_abstracts)
    
    print_time("Done, saving results to output file")
    print("----------------------------------------------")
    
    # Save the embeddings to a numpy file
    np.savez_compressed(args.output_file, embeddings=np_embedded, keys=np_pmids)
#!/usr/bin/env python

'''
This script takes a set of PMIDs and retrieves the abstracts from the NCBI database.
These abstracts are then embedded using the TF-IDF model and saved to a CSV file where the first column is the PMID and the rest of the columns are the embeddings.
The script has five required and three optional arguments. ::

    Required:
    
    -p: The path to the PMIDs file
    -d: The path to the database file
    -o: The name of the output NPZ file

    Optional:
    --save-model: Name for the saved model
    --load-model: Name of the model to load
    --ngrams: How many ngrams to use (default 3)

    Usage:
    
    python3 PMID2Tfidf.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_tfidf_embeddings.npz

    If you want to save the trained model:
    python3 PMID2Tfidf.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_tfidf_embeddings.npz --save-model model_name.joblib

    If you want to use a pre-trained model:
    python3 PMID2Tfidf.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_tfidf_embeddings.npz --load-model model_name.joblib
    
'''

import argparse
from datetime import datetime
import ijson
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import load, dump
from scipy.sparse import sparray
import numpy as np

def print_time(message: str) -> None:
    # Make docstring with rst syntax
    '''
    Print the current time and a message.\n
    \n
    Parameters:\n
    - message: The message to print\n
    '''
    
    print(f"{datetime.now().time().strftime('%H:%M:%S')} - {message}")

def fit_model(abstracts, n_ngrams) -> TfidfVectorizer:
    # Make docstring with rst syntax
    '''
    Fit the TfidfVectorizer model.\n
    \n
    Parameters:\n
    - abstracts: abstracts to use for the fitting\n
    - n_ngrams: number of ngrams to use for the model
    \n
    Returns:\n
    - model: The TfidfVectorizer model
    '''
    
    # fit the model to given data

    abstract_list = list(abstracts.values())

    model = TfidfVectorizer(stop_words='english', ngram_range=(1, n_ngrams), min_df=0.0001, max_df=0.95) 
    model.fit(abstract_list)

    return model

def embed_abstracts(model, abstracts) -> tuple[sparray, np.ndarray]:
    # Make docstring with rst syntax
    '''
    Embed the abstracts using TfidfVectorizer model.\n
    \n
    Parameters:\n
    - model: The TfidfVectorizer model\n
    - abstracts: Dict of PMID keys and abstracts\n
    \n
    Returns:\n
    - tf_ifd_matrix: The embeddings of the abstracts as TF-IDF matrix
    - np_pmids: The PMIDs as a numpy array
    '''

    abstract_list = list(abstracts.values())
    tf_idf_matrix = model.transform(abstract_list)

    print(f"{datetime.now().time().strftime('%H:%M:%S')} - Resulting tf idf matrix shape: {tf_idf_matrix.shape}")

    np_pmids = np.array(list(abstracts.keys()))
    
    # Convert the sparse matrix to a numpy array
    np_matrix = tf_idf_matrix.toarray()

    return np_matrix, np_pmids


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

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pmid_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-d", dest="pmid_database", required=True, help="Provide the path to the datafolder")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output NPZ file")
    parser.add_argument("--save-model", dest="save_model", required=False, default=None, help="Provide the path to save the model")
    parser.add_argument("--load-model", dest="load_model", required=False, default=None, help="Provide the path to load the model from")
    parser.add_argument("--ngrams", dest="ngrams", required=False, type=int, default=3, help="Number of ngrams to use")

    # Read arguments from the command line
    args=parser.parse_args()

    # Read the positive and negative PMIDs from the txt files
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
        
    # Read the positive and negative database JSON files
    pmid_abstracts, abs_none = get_abstracts(pmids=pmids, database_file=args.pmid_database)
    
    print_time(f"PMIDs with no abstracts: {abs_none}")

    print_time("Loading model...")
    
    # Use the model if it is provided
    if args.load_model:
        model = load(args.load_model)
        print_time("Done loading model")

    # Train the model if it is not provided
    else:
        model = fit_model(pmid_abstracts, n_ngrams=args.ngrams)
        print_time("Done training model")
    
    print("-----------------------------")

    if args.save_model:
        dump(model, args.save_model)
        print_time(f"Model was saved to {args.save_model}")

    print_time("Embedding abstracts...")
    
    # Call the function
    np_matrix, np_pmids = embed_abstracts(model=model, abstracts=pmid_abstracts)
    
    print_time("Done, saving results to output file")
    print("----------------------------------------------")

    # Save the embeddings and pmids to a numpy file
    np.savez_compressed(args.output_file, embeddings=np_matrix, keys=np_pmids)
#!/usr/bin/env python

'''
This script takes a set of PMIDs and retrieves the abstracts from the NCBI database.
These abstracts are then embedded using the TF-IDF model and saved to a CSV file where the first column is the PMID and the rest of the columns are the embeddings.
The script has five required and three optional arguments. ::

    Required:
    
    -p: The path to the PMIDs file
    -d: The path to the database file
    -o: The name of the output NPZ file
    -e: The type of embedding to use (abstract for only abstracts, title for only titles, title_abstract for abstracts and titles)


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
from joblib import load, dump
import numpy as np
from scipy.sparse import sparray
from sklearn.feature_extraction.text import TfidfVectorizer

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

def embed_texts(model, texts) -> tuple[sparray, np.ndarray]:
    # Make docstring with rst syntax
    '''
    Embed the abstracts using TfidfVectorizer model.\n
    \n
    Parameters:\n
    - model: The TfidfVectorizer model\n
    - texts: Dict of PMID keys and texts\n
    \n
    Returns:\n
    - tf_ifd_matrix: The embeddings of the texts as TF-IDF matrix
    - np_pmids: The PMIDs as a numpy array
    '''

    text_list = list(texts.values())
    tf_idf_matrix = model.transform(text_list)

    print(f"{datetime.now().time().strftime('%H:%M:%S')} - Resulting tf idf matrix shape: {tf_idf_matrix.shape}")

    np_pmids = np.array(list(texts.keys()))
    
    # Convert the sparse matrix to a numpy array
    np_matrix = tf_idf_matrix.toarray()

    return np_matrix, np_pmids


def get_texts(pmids: list, database_file: str, embedding_type: str) -> dict:
    # Make docstring with rst syntax
    '''
    Get the texts from the JSON database file for a list of PMIDs.\n
    \n
    Parameters:\n
    - pmids: A list of PMIDs\n
    - database_file: The path to the JSON database file\n
    - embedding_type: The type of embedding to use (1 for only abstracts, 2 for abstracts and titles)\n
    \n
    Returns:\n
    - pmid_texts: A dictionary with PMIDs as keys and texts as values\n
    - none_abstracts: The number of PMIDs with no abstracts\n
    - none_titles: The number of PMIDs with no titles\n
    '''
    
    pmid_texts = dict()
    none_abstracts = 0
    none_titles = 0
    
    # Stream over the JSON file
    with open(database_file, 'rb') as file:
        # Create a parser object over the JSON file
        parser = ijson.items(file, 'item')
        
        # Iterate over the JSON objects
        for item in parser:
            if item['pmid'] in pmids:
                text = ''
                store = False
                if embedding_type not in ["abstract", "title", "title_abstract"]:
                    raise ValueError("Invalid embedding type. Please use abstract, title or title_abstract")
                
                if embedding_type == "title_abstract" or embedding_type == "title":
                    if item['title'] is not None:
                        text += item['title']
                        store = True
                    else:
                        none_titles += 1
                        
                if embedding_type == "title_abstract" or embedding_type == "abstract":
                    if item['abstract'] is not None:
                        text += item['abstract']
                        store = True
                    else:
                        none_abstracts += 1
                    
                if store: 
                    pmid_texts[item['pmid']] = text                       
    
    return pmid_texts, none_abstracts, none_titles

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pmid_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-d", dest="pmid_database", required=True, help="Provide the path to the datafolder")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output NPZ file")
    parser.add_argument("-e", dest="embedding_type", required=True, default="abstract", help="Mode for embedding: abstract for only abstracts, title for only titles, or title_abstract for abstracts and titles")

    
    parser.add_argument("--save-model", dest="save_model", required=False, default=None, help="Provide the path to save the model")
    parser.add_argument("--load-model", dest="load_model", required=False, default=None, help="Provide the path to load the model from")
    parser.add_argument("--ngrams", dest="ngrams", required=False, type=int, default=3, help="Number of ngrams to use")

    # Read arguments from the command line
    args=parser.parse_args()

    # Read the positive and negative PMIDs from the txt files
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
        
    # Read the positive and negative database JSON files
    pmid_texts, abs_none, title_none = get_texts(
        pmids=pmids, 
        database_file=args.pmid_database, 
        embedding_type=args.embedding_type
        )
    
    if args.embedding_type == "title_abstract":
        print_time(f"PMIDs with no titles: {title_none}")
        print_time(f"PMIDs with no abstracts: {abs_none}")
    elif args.embedding_type == "title":
        print_time(f"PMIDs with no titles: {title_none}")
    else:
        print_time(f"PMIDs with no abstracts: {abs_none}")

    print_time("Loading model...")
    
    # Use the model if it is provided
    if args.load_model:
        model = load(args.load_model)
        print_time("Done loading model")

    # Train the model if it is not provided
    else:
        model = fit_model(pmid_texts, n_ngrams=args.ngrams)
        print_time("Done training model")
    
    print("-----------------------------")

    if args.save_model:
        dump(model, args.save_model)
        print_time(f"Model was saved to {args.save_model}")

    print_time("Embedding abstracts...")
    
    # Call the function
    np_matrix, np_pmids = embed_texts(model=model, texts=pmid_texts)
    
    print_time("Done, saving results to output file")

    # Save the embeddings and pmids to a numpy file
    np.savez_compressed(args.output_file, embeddings=np_matrix, keys=np_pmids)
    
    print_time(f"Embeddings saved to {args.output_file}")
    print("----------------------------------------------")
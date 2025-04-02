#!/usr/bin/env python

'''
This script takes a set of PMIDs and retrieves the abstracts from the NCBI database.
These abstracts are then embedded using the SentenceTransformer model and saved to a Numpy file where the first column is the PMID and the rest of the columns are the embeddings.
The script has five required arguments. ::

    Required:
    
    -p: The path to the PMIDs file
    -d: The path to the database file
    -o: The name of the output file
    -e: The type of embedding to use (abstract for only abstracts, title for only titles, title_abstract for abstracts and titles)
    -m: The key of the SentenceTransformer model to use. Options are minilml6, minilml12, mpnetv2, roberta, biobert, pubmedbert
    
    Usage:
    
    python3 PMID2Embed.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_test_embeddings.npz -e title_abstract -m minilml6
    
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
    Model options are:\n
    - all-MiniLM-L6-v2\n
    - all-MiniLM-L12-v2\n
    - all-mpnet-base-v2\n
    - all-distilroberta-v1\n
    - dmis-lab/biobert-v1.1\n
    - NeuML/pubmedbert-base-embeddings\n
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

def get_texts(pmids: list, database_file: str, embedding_type: str) -> dict:
    # Make docstring with rst syntax
    '''
    Get the texts from the JSON database file for a list of PMIDs.\n
    \n
    Parameters:\n
    - pmids: A list of PMIDs\n
    - database_file: The path to the JSON database file\n
    - embedding_type: The type of embedding to use (abstract for only abstracts, title_abstract for abstracts and titles)\n
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

def embed_texts(model, texts: dict) -> np.ndarray:
    # Make docstring with rst syntax
    '''
    Embed a dictionary of abstracts using the SentenceTransformer model.\n
    \n
    Parameters:\n
    - model: The SentenceTransformer model\n
    - texts: A dictionary with PMIDs as keys and texts as values\n
    \n
    Returns:\n
    - np_embedded: A numpy array with embeddings
    - np_pmids: A numpy array with PMIDs
    '''
    
    # Get the abstracts as a list
    abstract_list = list(texts.values())
    
    # Embed the abstracts with parallization
    np_embedded = model.encode(abstract_list, show_progress_bar=False)
    
    # Make np array with shape (123,) with PMIDs
    np_pmids = np.array(list(texts.keys()))
        
    return np_embedded, np_pmids

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pmid_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-d", dest="pmid_database", required=True, help="Provide the path to the datafolder")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output .npy file")
    parser.add_argument("-e", dest="embedding_type", required=True, default="abstract", help="Mode for embedding: abstract for only abstracts, title for only titles, or title_abstract for abstracts and titles")
    parser.add_argument("-m", dest="model_name", required=False, default="minilml6", help="The key of the SentenceTransformer model to use. Options are minilml6, minilml12, mpnetv2, roberta, biobert, pubmedbert")
    
    # Read arguments from the command line
    args=parser.parse_args()
    
    model_options = {
        "minilml6": "all-MiniLM-L6-v2",
        "minilml12": "all-MiniLM-L12-v2",
        "mpnetv2": "all-mpnet-base-v2",
        "roberta": "all-distilroberta-v1",
        "biobert": "dmis-lab/biobert-v1.1",
        "pubmedbert": "NeuML/pubmedbert-base-embeddings"
    }

    # Read the PMIDs from the txt files
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
        
    print_time("Getting abstracts from the database...")    
        
    # Read the database JSON files
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
    print(args.model_name)
    if args.model_name is not None and args.model_name in model_options:
        model_name = model_options[args.model_name]
    else:
        model_name = model_options["minilm"]
        
    print(f"Using Transformer model: {model_name}")
        
    model = load_model(model_name = model_name)
    
    print_time("Done loading model")
    print("-----------------------------")

    print_time("Embedding abstracts...")
    
    print_time(f"Total number of texts: {len(pmid_texts)}")
    
    # Call the function
    np_embedded, np_pmids = embed_texts(model=model, texts=pmid_texts)
    
    print_time("Done, saving results to output file")
    
    # Save the embeddings to a numpy file
    np.savez_compressed(args.output_file, embeddings=np_embedded, keys=np_pmids)
    
    print_time(f"Embeddings saved to {args.output_file}")
    print("----------------------------------------------")
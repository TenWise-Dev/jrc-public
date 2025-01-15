#!/usr/bin/env python

'''
This script a set of PMIDs and retrieves the abstracts from the NCBI database.
These abstracts are then embedded using the Doc2Vec model and saved to a CSV file where the first column is the PMID and the rest of the columns are the embeddings.
The script has five required and three optional arguments. ::

    Required:
    
    -p: The path to the PMIDs file
    -d: The path to the database file
    -o: The name of the output file
    -e: The type of embedding to use (abstract for only abstracts, title for only titles, title_abstract for abstracts and titles)

    Optional:
    --save-model: Name for the saved model
    --load-model: Name of the model to load
    --epochs: Number of epochs for training the model (default 40)
    --workers: Number of workers for training the model (default 4)
    
    Usage:
    
    python3 PMID2Doc2Vec.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_doc2vec_embeddings.npz -e 1

    If you want to save the trained model:
    python3 PMID2Doc2Vec.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_doc2vec_embeddings.npz --save-model doc2vec.model --epochs 50 --workers 8 -e 1

    If you want to use a pre-trained model:
    python3 PMID2Doc2Vec.py -p ../example/demo_pmids.txt -d ../example/demo_database.json -o ../YOUR_FOLDER/demo_doc2vec_embeddings.npz --load-model model_name.model -e 1
    
'''

import argparse
from datetime import datetime
import ijson
from gensim.parsing.preprocessing import remove_stopwords
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
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

def fit_model(abstracts, n_epochs, n_workers) ->  Doc2Vec:
    # Make docstring with rst syntax
    '''
    Fit the Doc2Vec model.\n
    \n
    Parameters:\n
    - abstracts: dict of given pmids and abstracts for training the model.\n
    - n_epochs: number of epochs for training the model\n
    - n_workers: number of workers for training the model\n
    \n
    Returns:\n
    - model: The gensim Doc2Vec model
    '''

    tagged_documents = []
    abstract_list = list(abstracts.values())

    for index, abstract in zip(abstracts.keys(), abstract_list):
        ab = remove_stopwords(abstract)
        tokens = simple_preprocess(ab)
        doc = TaggedDocument(tokens, [index]) # tag is pmid 
        tagged_documents.append(doc)

    print(f"{datetime.now().time().strftime('%H:%M:%S')} - Fitting Doc2Vec model...")

    model = Doc2Vec(vector_size=50, min_count=3, epochs=n_epochs, workers=n_workers) 
    model.build_vocab(tagged_documents)
    model.train(tagged_documents, total_examples=model.corpus_count, epochs=model.epochs)
    
    return model

def embed_texts(model, texts) -> list[str]:
    # Make docstring with rst syntax
    '''
    Embed the texts using densim Doc2Vec model.\n
    \n
    Parameters:\n
    - model: The Doc2Vec model\n
    - texts: Dict of PMID keys and texts\n
    \n
    Returns:\n
    - document_embeddings: The embeddings of the texts as np array
    - np_pmids: The PMIDs as a numpy array
    '''
    
    pmids = list(texts.keys())
    embeddings = []
    for pmid in pmids:
        if pmid in model.dv: # If we are embedding abstract that was used in the training
            embeddings.append(model.dv[pmid]) # we can read it directly from the model
        else:
            # otherwise we need to embed it:
            text = remove_stopwords(texts[pmid])
            tokens = simple_preprocess(text)
            embeddings.append(model.infer_vector(tokens))

    # Make np array out of the pmids
    np_pmids = np.array(list(texts.keys()))
    
    document_embeddings = np.array(embeddings)

    return document_embeddings, np_pmids



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
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output CSV file")
    parser.add_argument("-e", dest="embedding_type", required=True, default="abstract", help="Mode for embedding: abstract for only abstracts, title for only titles, or title_abstract for abstracts and titles")
    
    parser.add_argument("--save-model", dest="save_model", required=False, default=None, help="Provide the path to save the model")
    parser.add_argument("--load-model", dest="load_model", required=False, default=None, help="Provide the path to load the model from")
    parser.add_argument("--epochs", dest="epochs", required=False, type=int, default=40, help="Number of epochs for training the model")
    parser.add_argument("--workers", dest="workers", required=False, type=int, default=4, help="Number of workers for training the model")

    # Read arguments from the command line
    args=parser.parse_args()

    # Read the PMIDs from the txt file
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
      
    print_time(f"PMIDs read from file: {len(pmids)}" )  
    
    # Read the database JSON file
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
    
    print_time(f"Loading model..." )

    print(f"{datetime.now().time().strftime('%H:%M:%S')} - Loading model...")
    
    # Use the model if it is provided
    if args.load_model:
        model = Doc2Vec.load(args.load_model)
        print_time(f"Done loading model")

    # Train the model if it is not provided
    else:
        model = fit_model(pmid_texts, n_epochs=args.epochs, n_workers=args.workers)
        print_time(f"Done training model")
    
    print("-----------------------------")

    if args.save_model:
        model.save(args.save_model)
        print_time(f"Model was saved to {args.save_model}")


    print_time("Embedding abstracts...")
    
    # Call the embed function
    texts_embedded, np_pmids = embed_texts(model=model, texts=pmid_texts)
    
    print_time("Done, saving results to output file")
    print("----------------------------------------------")

    np.savez_compressed(args.output_file, embeddings=texts_embedded, keys=np_pmids)
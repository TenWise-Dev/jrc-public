#!/usr/bin/env python

"""
This script loads a set of embeddings and a set of models and predicts the class of the embeddings using the provided model.
The script has three required arguments. ::

    Required:
    
    -e : The path to the embedding set .npz file
    -m : The path to the model pickle file
    -o : The name of the output JSON file
    
    Usage:
    
    python3 PMID2Predict.py -e ../example/demo_pos_embeddings.npz -m ../example/models/randomforest.pkl -o ../YOUR_FOLDER/demo_predictions.json

"""

import pickle
import argparse
import json
import numpy as np
import pandas as pd
from datetime import datetime

def print_time(message: str) -> None:
    # Make docstring with rst syntax
    '''
    Print the current time and a message.\n
    \n
    Parameters:\n
    - message: The message to print\n
    '''
    
    print(f"{datetime.now().time().strftime('%H:%M:%S')} - {message}")

def load_embeddings(embedding_file: str) -> np.ndarray:
    # Make docstring with rst syntax
    """
    Load the embeddings from a numpy npz file.\n
    \n
    Parameters:\n
    - embedding_file: The path to the embedding set .npz file\n
    \n
    Returns:\n
    - embeddings: The embeddings as a numpy array with the pmids and embeddings
    """
    # Load the embeddings
    embeddings = np.load(embedding_file, allow_pickle=True)
    return embeddings

def predict_embeddings(embeddings: np.ndarray, models_file: str, output_file: str) -> None:
    # Make docstring with rst syntax
    """
    Predict the class of the embeddings using the provided model.\n
    \n
    Parameters:\n
    - embeddings: The embeddings as a numpy array with the pmids and embeddings\n
    - models_file: The path to the model\n
    \n
    Returns:\n
    - results: The predictions and probabilities
    """
    # Load the model
    with open(models_file, 'rb') as file:
        model = pickle.load(file)
    
    predictions = model.predict(embeddings['embeddings'])
    probabilities = model.predict_proba(embeddings['embeddings'])

    # Make a dataframe for results, first column of embeddings is PMID
    df_results = pd.DataFrame(embeddings['keys'], columns=["PMID"])
    
    # Add the predictions to the dataframe
    df_results["Prediction"] = predictions
    df_results["Probability"] = np.max(probabilities, axis=1)
    
    # Get model name from the model object
    model_name = str(model).split("(")[0]
    
    # Add column with model name to the dataframe
    df_results["Model"] = model_name
    
    # Convert the dataframe to a dictionary with the pmid as key and the rest as values
    df_results = df_results[["PMID", "Prediction", "Probability", "Model"]].set_index("PMID").T.to_dict()
    
    # Save the dictionary to a JSON file
    with open(output_file, 'w') as file:
        json.dump(df_results, file, indent=4)
    
    pass

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-e", dest="embedding_file", required=True, help="Provide the path to the embedding set .npz file")
    parser.add_argument("-m", dest="models_file", required=True, help="Provide the path to the model")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output JSON file")

    # Read arguments from the command line
    args=parser.parse_args()
    
    print_time("Start with loading embeddings")
        
    # Retrieve embeddings from the CSV file
    embeddings = load_embeddings(embedding_file=args.embedding_file)
    
    print_time("Finished loading embeddings")
    
    # Predict the class of the embeddings using the provided model and save the results to a dictionary
    print_time("Start with predicting embeddings")    
    predict_embeddings(embeddings=embeddings, models_file=args.models_file, output_file=args.output_file)
    print_time("Finished predicting embeddings")
    
    
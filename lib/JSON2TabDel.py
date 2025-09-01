#!/usr/bin/env python

'''
This script is used to convert the results from the different models and embeddings to a CSV file.
This file is stored again in the results directory.
The script has two required arguments. ::

    Required:
    
    -r : The path to the results directory
    -o : The path to the output file
    
    Usage:
    
    python3 JSON2TabDel.py -r ../example/results/ -o ../example/demo_results.csv

'''
import argparse
import pandas as pd
import os

def load_results(resultdir: str, embeddings: list, models: list) -> pd.DataFrame:
    """
    Function to load the results from the different models and embeddings\n
    \n
    Parameters:\n
    - resultdir: The directory with the results\n
    - embeddings: The list of embeddings\n
    - models: The list of models\n
    \n
    Returns:\n
    - The DataFrame with the results
    """
    # Create an empty dictionary to store the results
    results = {}
    
    # Iterate over the embeddings
    for embed in embeddings:
        # Iterate over the models
        for mod in models:
            # Create the filename
            filename = resultdir + "/scores_" + mod + "_" + embed +".json"
            
            if not os.path.exists(filename):
                print(f"File {filename} does not exist. Skipping...")
                continue
            
            # Load the data into a DataFrame
            df = pd.read_json(filename, convert_axes=False).transpose().rename_axis("PMID").reset_index()
            
            # Rename the columns
            df.columns = ['pmid','prediction', 'score', 'method']
            
            # Add the embedding
            df['embedding'] = embed
            
            # Store the results
            results[filename] = df
    
    # Concatenate the results
    df = pd.concat(results.values(), axis=0, ignore_index=True)
    
    return df

def process_df(df: pd.DataFrame) -> tuple:
    """
    Function to process the DataFrame and calculate the normalized mean percentile score\n
    \n
    Parameters:\n
    - df: The DataFrame with the results\n
    - resultdir: The directory with the results\n
    \n
    Returns:\n
    - The merged DataFrame with the average score\n
    - The DataFrame with the abstracts
    """
    
    # Normalize score to 0 - 1 range where 0 is a high score for a negative prediction and 1 is a high score for a positive prediction
    # Use 'prediction' column to determine if a score is a positive or negative prediction
    df['normscore'] = df['score']
    df.loc[df['prediction'] == 0, 'normscore'] = 1 - df['normscore']
        
    return df

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-r", dest="results_directory", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the path to the output file")
    
    # Read arguments from the command line
    args=parser.parse_args()

    # First we read in all the json formatted results
    embeddings = ['transformer' ,'doc2vec','tfidf'] 
    models = ['adaboost','gradientboost','logistic_regression','randomforest']
    
    # Load the results
    df = load_results(resultdir=args.results_directory, embeddings=embeddings, models=models)
    
    # Merge with the scores and calculate the average score
    # The average score is calculated by multiplying the prediction with the score
    df_processed = process_df(df=df)

    # Save the results to a csv file
    df_processed.to_csv(args.results_directory + args.output_file, index=False, sep='\t')

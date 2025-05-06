#!/usr/bin/env python

'''
This script is used to convert the results from a tab-delimited file to a CSV file using a mean percentile score.
The script has two required arguments. ::
    
    Required:
    
    -r : The path to the tab-delimited file
    -o : The path to the output file
    
    Usage:
    
    python3 CalculateFinalScore.py -r ../example/demo_results.csv -o ../example/demo_results.csv

'''
import argparse
import pandas as pd

def load_results(result_file: str) -> pd.DataFrame:
    """
    Function to load the results from the different models and embeddings\n
    \n
    Parameters:\n
    - result_file: The path to the tab-delimited file\n
    \n
    Returns:\n
    - The DataFrame with the results
    """
    
    # Load the data into a DataFrame
    df = pd.read_csv(result_file, sep='\t')
    
    return df

def process_df(df: pd.DataFrame, max_scores: pd.DataFrame) -> tuple:
    """
    Function to process the DataFrame and calculate the normalized mean percentile score\n
    \n
    Parameters:\n
    - df: The DataFrame with the results
    \n
    Returns:\n
    - The DataFrame with the results
    """
    
    # Group by embedding and method
    # Calculate max score to normalize with mean percentile method
    df = pd.merge(df, max_scores, on=['embedding', 'method'])
    
    # Normalize the score with the max score
    df['percentile_score'] = df['normscore'] / df['max_score']
    
    # Ensure the percentiles are at least 0 and at most 1
    df['percentile_score'] = df['percentile_score'].clip(lower=0, upper=1)
    
    merged_df = df.copy()
    
    # Calculate the mean percentile score for each pmid (method, embedding)
    merged_df['model_score'] = df.groupby(['pmid'])['percentile_score'].transform('mean')
    
    
    # Remove prediction, method, embedding columns
    merged_df = merged_df.drop(columns=['prediction', 'method', 'embedding'])
    
    # Remove score columns
    merged_df = merged_df.drop(columns=['score', 'normscore', 'max_score', 'percentile_score'])
    merged_df = merged_df.drop_duplicates()
    
    nr_pos = df.groupby(['pmid'])['prediction'].agg(['sum'])
    
    df_merge = pd.merge(merged_df, nr_pos, on='pmid')
    df_merge = df_merge.reset_index()  

    df_merge['pmid'] = df_merge.pmid.astype(int)

    return df_merge

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-r", dest="results_file", required=True, help="Provide the path to the tab-delimited file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the path to the output file")
    
    # Read arguments from the command line
    args=parser.parse_args()

    # Load the results
    df = load_results(result_file=args.results_file)
    
    iteration_id = "iteration3"
    
    # Read precomputed max_scores.csv to get the max scores for each method and embedding
    max_scores = pd.read_csv(f'lib/max_scores_{iteration_id}.csv')
    
    # The model score is calculated by taking the mean of the percentile scores
    df_merge = process_df(df=df, max_scores=max_scores)
        
    # Sort on model score
    df_merge = df_merge.sort_values(by ='model_score', ascending=False)

    # Save the results to an Excel
    df_merge.to_csv(args.output_file, index=False)

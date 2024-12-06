'''
This script is used to convert the results from the different models and embeddings to an Excel file.
This file is stored again in the results directory.
The script has two required arguments. ::

    Required:
    
    -r : The path to the results directory
    -i : Provide boolean to indicate if intermediate storage is required
    
    Usage:
    
    python3 results2csv.py -r ../example/results/ -d ../example/demo_database.json -i True

'''
import argparse
import pandas as pd

def map_prediction(value: int) -> int:
    """
    Function to map the prediction to a multiplier for the score\n
    \n
    Parameters:\n
    - value: The prediction value\n
    \n
    Returns:\n
    - 1 if value is 1, -1 otherwise
    """
    return 1 if value == 1 else -1

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

def process_df(df: pd.DataFrame, resultdir: str, json_file: str) -> tuple:
    """
    Function to process the DataFrame and calculate the average score\n
    \n
    Parameters:\n
    - df: The DataFrame with the results\n
    - resultdir: The directory with the results\n
    \n
    Returns:\n
    - The merged DataFrame with the average score\n
    - The DataFrame with the abstracts
    """
    # Apply the function to create the new column
    df['multiplier'] = df['prediction'].apply(map_prediction)
 
    #The score can now be calculated by multiplying the multiplier by the score
    df['pos_score'] = df.score * df.multiplier

    # Now we can calculate the average
    avg_scores = df.groupby(['pmid'])['pos_score'].agg(['mean', 'std'])
    nr_pos = df.groupby(['pmid'])['prediction'].agg(['sum'])
    
    df_merge = pd.merge(avg_scores, nr_pos, on='pmid')
    df_merge = df_merge.rename_axis("pmid").reset_index()  
    
    # Read JSON file with abstracts into a DataFrame
    df_abs = pd.read_json(json_file, convert_axes=False)
    
    df_merge['pmid'] = df_merge.pmid.astype(int)
    
    df_abs.pmid.astype(int)
    
    # Merge with the scores
    df_merge = pd.merge(df_merge , df_abs, on='pmid')

    return df_merge, df_abs

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-r", dest="results_directory", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-i", dest="intermed_storage", required=True, help="Provide boolean to indicate if intermediate storage is required")
    parser.add_argument("-d", dest="json_file", required=True, help="Provide the path to the positive pmid file")
    
    # Read arguments from the command line
    args=parser.parse_args()

    # First we read in all the json formatted results
    embeddings = ['transformer' ,'doc2vec','tfid', 'bow_pos', 'bow_neg']
    models = ['adaboost','gradientboost','logistic_regression','randomforest']
    
    # Load the results
    df = load_results(resultdir=args.results_directory, embeddings=embeddings, models=models)
    
    # Merge with the scores and calculate the average score
    # The average score is calculated by multiplying the prediction with the score
    df_merge, df_abs = process_df(df=df, resultdir=args.results_directory, json_file=args.json_file)

    if args.intermed_storage:
        df['pmid'] = df.pmid.astype(int)
        df = df.merge(df_abs, on='pmid')
        # Sort df by pos_score for intermediate storage but keep pmid order
        df = df.sort_values(by='pos_score', ascending=False)
        df = df.drop(columns=['multiplier', 'score'])
        df.rename(columns={'pos_score': 'score'}, inplace=True)
        
        # sort by pmid, method, embedding
        df = df.sort_values(by=['pmid', 'method', 'embedding'])
        df.to_csv(args.results_directory +'/intermediate_storage.csv', index=False)
        
    # Sort on mean score
    df_merge = df_merge.sort_values(by ='mean')

    # Select top30 of each category
    df_tokeep =  pd.concat([df_merge.head(30), df_merge.tail(30)], ignore_index=True).sample(frac=1).reset_index(drop=True)
    
    # Save the results to an Excel
    df_merge.to_csv(args.results_directory +'/merged_and_scored.csv', index=False)
    df_tokeep.drop(columns=["mean","std","sum"]).to_csv(args.results_directory +'/for_validation.csv', index=False)

#!/usr/bin/env python

'''
This script assesses a JSON database file and returns a JSON file with the multiple metrics.\n
The metrics include the number of missing values, the number of unique values, the number of duplicates, and the number of unique values for important columns.\n

The script has two required arguments. ::

    Required:
    
    -j : The path to the Database JSON file
    -o : The path to the Output JSON file
    
    Usage:
    
    python3 DatabaseValidation.py -j ../example/demo_database.json -o ../YOUR_FOLDER/demo_output.json
'''

import ijson
import json
from tqdm import tqdm
import pandas as pd

import argparse

def process_database(database_file: str) -> pd.DataFrame:
    # Make docstring with rst syntax
    """
    This function assesses the database file and returns a DataFrame with metadata information.\n
    \n
    Parameters:\n
    - database_file: The path to the database file\n
    \n
    Returns:\n
    - df: A DataFrame with the following columns: pmid, doi, title, author, abstract, year, first_author, mesh, is_oa
    """

    df_metadata = pd.DataFrame(columns=['pmid', 'doi', 'pmcid', 'title', 'author', 'abstract', 'year', 'first_author', 'mesh', 'is_oa'])

    # Stream over the JSON file
    with open(database_file, 'rb') as file:
        # Create a parser object over the JSON file
        parser = ijson.items(file, 'item')
        
        # Iterate over the JSON objects
        for item in tqdm(parser):
            # Create a dictionary to store the metadata
            metadata = {'pmid': None, 'doi': None, 'pmcid': None, 'title': None, 'author': None, 'abstract': None, 'year': None, 'first_author': None, 'mesh': None, 'is_oa': None}	
            for key in metadata.keys():
                try:
                    metadata[key] = item[key]
                except KeyError:
                    pass
            df_metadata = df_metadata._append(metadata, ignore_index=True)
            
    return df_metadata
        
def assess_database(df: pd.DataFrame) -> dict:
    # Make docstring with rst syntax
    """
    This function assesses a pandas dataframe to summarize quality of the data.\n
    It calculates the number of missing values, the number of unique values, the number of duplicates, and the number of unique values for each column.\n
    \n
    Parameters:\n
    - df: A pandas DataFrame\n
    \n
    Returns:\n
    - dict_assess: A dictionary with the following general keys: column, missing_values, unique_values, duplicates. Each column also has unique keys for specific information.
    """
    
    # Create a DataFrame to store the assessment
    df_assessed = {column: {'missing_values': None, 'unique_values': None, 'duplicates': None} for column in df.columns}
    
    # Iterate over the columns
    for column, metadata in tqdm(df_assessed.items()):
        if column in df.columns:
            # Calculate the number of missing values
            metadata['missing_values'] = int(df[column].isnull().sum())
            
            # Calculate the number of unique values
            metadata['unique_values'] = int(df[column].nunique())
            
            # Calculate the number of duplicates (exclude null values)
            non_null_values = df[column].dropna()
            
            metadata['duplicates'] = int(non_null_values.duplicated().sum())
                        
            # Replace all None values with ""
            df[column] = df[column].apply(lambda x: "" if x is None else x)
            
            # PMID, DOI, Title checks
            if column in ['pmid', 'doi', 'title']:
                # Get the pmids for the non-null values
                non_null_pmids = df.loc[non_null_values.index]['pmid']
                
                # Provide the pmids of the duplicates (not the null values)
                metadata['duplicated_pmids'] = non_null_pmids[non_null_values.duplicated()].tolist()
                
                # Provide the missing pmids
                metadata['missing_pmids'] = df[df[column].isnull()]['pmid'].tolist()
            
            # Abstract checks
            if column == 'abstract':
                # Calculate the average length of the abstracts in words (rounded to 0 decimals)
                metadata['avg_abstract_length'] = df[column].apply(lambda x: len(x.split())).mean()
                
                # Round to 0 decimals
                metadata['avg_abstract_length'] = round(metadata['avg_abstract_length'], 0)
                
                # Provide the missing pmids
                metadata['missing_pmids'] = df[df[column].isnull()]['pmid'].tolist()
            
            # First author checks
            if column == 'first_author':
                # Provide the missing pmids
                metadata['missing_pmids'] = df[df[column].isnull()]['pmid'].tolist()
            
            # Species, tissue, model, method checks
            if column in ['species']:
                # Provide a count of the unique values, first split on ;
                metadata['value_counts'] = df[column].apply(lambda x: x.split('; ')).explode().value_counts().to_dict()
                
            if column in ['method', 'model']:
                # Provide a count of the unique values, first split on ;
                metadata['value_counts'] = df[column].apply(lambda x: x.split(' / ')).explode().value_counts().to_dict()
            
            # Mesh checks
            if column == 'mesh':   
                # Provide the average number of mesh terms (first split on ;)
                metadata['avg_mesh_terms'] = df[column].apply(lambda x: len(x.split(';'))).mean()
                
                # Round to 0 decimals
                metadata['avg_mesh_terms'] = round(metadata['avg_mesh_terms'], 0)
            
            # Text availability checks
            if column == 'is_oa': 
                # Replace "" with false
                df[column] = df[column].apply(lambda x: False if x == "" else x)
                           
                # Provide the count of text availability
                metadata['is_oa'] = df[column].value_counts().to_dict()
            
            # Update the dictionary
            df_assessed[column] = metadata
            
    return df_assessed

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the Database JSON file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the path to the Output CSV file")

    # Read arguments from the command line
    args=parser.parse_args()
    
    # Check if output file exists, if so, remove it
    try:
        with open(args.output_file, 'r') as file:
            pass
        with open(args.output_file, 'w') as file:
            pass
    except FileNotFoundError:
        with open(args.output_file, 'w') as file:
            pass  
        
    print("Loading the database file...")
        
    # Assess the database file
    df_processed = process_database(args.json_file)
    
    print("Assessing the DataFrame...")
    
    # Assess the DataFrame
    df_assessed = assess_database(df_processed)
    
    # Save the DataFrame to a JSON file
    with open(args.output_file, 'w') as file:
        json.dump(df_assessed, file, indent=4)
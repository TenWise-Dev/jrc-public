#!/usr/bin/env python

'''
This script is used to create bar plots for each disease area and tag category with the top 25 tags based on the total score.

The script has three required arguments. ::

    Required:
    
    -j : The path to the Output JSON file
    -v : The version of the database
    -o : The path to the output folder
    
    Usage:
    
    python3 Tags2Plots.py -j ../YOUR_FOLDER/demo_output.json -v 2024_11_13 -o ../YOUR_FOLDER/plots

'''

import ijson
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Excluded OMICs for now
TAG_CATEGORIES = {
    "disease": "disease",
    "in_vitro": "model",
    "in_silico": "model",
    "in_chemico": "model",
    "human_anatomy": "human_anatomy"
}

def create_dataframe(database_file: str) -> pd.DataFrame:
    
    '''
    This function reads the database file and creates a long format dataframe with the following columns:\n
    - disease_area\n
    - pmid\n
    - tag_category\n
    - tag\n
    - score\n
    \n
    Parameters:\n
    - database_file: The path to the database file\n
    \n
    Returns:\n
    - df: A long format dataframe with the columns mentioned above
    '''
    
    # Create long format dataframe with: disease_area, pmid, tag_category, tag, score
    df_dict = {'disease_area': [], 'pmid': [], 'tag_category': [], 'tag': [], 'score': []}

    # Read the json database file
    with open(database_file, 'r') as f:
        # Create a parser object over the JSON file
        parser = ijson.items(f, 'item')
        
        # Iterate over the JSON objects
        for item in tqdm(parser):    
                    
            # Get the pmid
            pmid = item['pmid']
            
            # Get the source
            disease_area = item['disease_area'].split(";")[0]
            
            if 'tagging_scores' not in item:
                continue
            
            # Get tagging information and store it in the dataframe
            for tag_subcategory in item['tagging_scores']:
                subcategory = tag_subcategory.lower()
                if subcategory in TAG_CATEGORIES:
                    tag_category = TAG_CATEGORIES.get(subcategory)
                    
                    for tag in item['tagging_scores'][tag_subcategory]:
                        df_dict['disease_area'].append(disease_area)
                        df_dict['pmid'].append(pmid)
                        df_dict['tag_category'].append(tag_category)
                        
                        # Make sure to lowercase the tag
                        df_dict['tag'].append(tag.lower())                        
                        df_dict['score'].append(item['tagging_scores'][tag_subcategory][tag])
                        
    # Create a dataframe
    df = pd.DataFrame(df_dict)

    # Group by disease_area, tag_category, tag and calculate the total score
    df = df.groupby(['disease_area', 'tag_category', 'tag']).agg({'score': 'sum'}).reset_index()

    # Create log2 score column
    df['log2_score'] = np.log2(df['score'] + 1)
    
    return df

def create_plots(df: pd.DataFrame, version: str, output_folder: str) -> None:
        
    '''
    This function creates bar plots for each disease area and tag category with the top 25 tags based on the total score.\n
    The plots are saved in the plots folder.\n
    \n
    Parameters:\n
    - df: A long format dataframe with the columns mentioned above\n
    - version: The version of the database\n
    - output_folder: The path to the output folder\n
    \n
    Returns:\n
    - None
    '''
        
    # Get the unique disease areas
    disease_areas = df['disease_area'].unique()
        
    # Get the unique categories and assign a color to each category
    unique_categories = df['tag_category'].unique()
    category_colors = {category.lower(): plt.cm.tab20(i) for i, category in enumerate(unique_categories)}

    # Loop over all disease areas
    for disease_area in disease_areas:
        df_disease_area = df[df['disease_area'] == disease_area].copy()
            
        df_disease_area['tag_category'] = df_disease_area['tag_category'].str.lower()
        
        # Group by tag category and plot the total score for each tag category
        df_disease_area_grouped = df_disease_area.groupby('tag_category').sum()
        included_categories = df_disease_area_grouped.index
        
        for tag_category in df_disease_area['tag_category'].unique():
            # Only keep the tag category
            df_filtered_tags = df_disease_area[df_disease_area['tag_category'] == tag_category]
            
            # Sort the tags by score and keep the top n
            top_n = 25
            df_disease_area_filtered = df_filtered_tags.sort_values('log2_score', ascending=True).tail(top_n)
            
            plt.barh(df_disease_area_filtered['tag'], df_disease_area_filtered['log2_score'])
            
            # Color the bars
            colors = [category_colors[category] 
                    for category in included_categories]
            for i, bar in enumerate(plt.gca().patches):
                bar.set_color(colors[i % len(colors)])
            
            # Set the title and labels
            plt.title(f'Disease Area: {disease_area} - {tag_category} Tags')
            plt.xlabel('Total score (log2)')
            plt.ylabel('Tag')
            
            # Replace spaces with underscores
            save_name = tag_category.replace(" ", "_")
            
            # Save the plot to a file
            plt.savefig(f'{output_folder}/{version}/tag_scores_{disease_area}_{save_name}_{version}.png', bbox_inches='tight')
            
            # Remove the plot but don't print it
            plt.close()
        
        
if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the Output JSON file")
    parser.add_argument("-v", dest="version", required=True, help="Provide the version of the database")
    parser.add_argument("-o", dest="output_folder", required=True, help="Provide the path to the output folder")
    

    # Read arguments from the command line
    args=parser.parse_args()
    
    # Create a dataframe
    df = create_dataframe(database_file=args.json_file)
    
    # Create and save plots
    create_plots(df=df, version=args.version, output_folder=args.output_folder)
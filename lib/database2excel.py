#!/usr/bin/env python

'''
This script takes modelling results and present the data in an highlighted HTML file

The start of the presentation layer is a set of prediction scores
This is indicated by the model_results_dir

'''
import argparse
import sys
import pandas as pd

def map_prediction(value):
    return 1 if value == 1 else -1

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", dest="jsondb_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-o", dest="output_file", required=True, help="Provide the path to the positive pmid file")
    #parser.add_argument("-o", dest="output_directory", required=True, help="Provide the path to the positive pmid file")
    # parser.add_argument("-d", dest="pmid_database", required=True, help="Provide the path to the datafolder")
    # parser.add_argument("-o", dest="output_file", required=True, help="Provide the name of the output .npy file")
    
    # Read arguments from the command line
    args=parser.parse_args()

    df_abs = pd.read_json(args.jsondb_file, convert_axes=False)
    print(df_abs)
    df_abs.to_excel(args.results_directory +'/'+args.prefix+ '_merged_and_scored.xlsx', index=False)
#     df_merge['pmid'] = df_merge.pmid.astype(int)
#     #print(df_merge)
#     df_abs.pmid.astype(int)
#     # Merge with the scores
#     df_merge = pd.merge(df_merge , df_abs, on='pmid')

# #    xlsxfile = df_merge.to_csv(args.output_directory, +'/merged_and_scored.csv')

#     # Sort on mean score
#     df_merge = df_merge.sort_values(by ='mean')

#     # Select top30 of each category
#     df_tokeep =  pd.concat([df_merge.head(30), df_merge.tail(30)], ignore_index=True).sample(frac=1).reset_index(drop=True)
    

#     
#     df_tokeep.drop(columns=["mean","std","sum"]).to_excel(args.results_directory +'/'+args.prefix+'_for_validation.xlsx', index=False)

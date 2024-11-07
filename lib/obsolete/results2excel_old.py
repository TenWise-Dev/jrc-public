'''
This script takes modelling results and present the data in an highlighted HTML file

The start of the presentation layer is a set of prediction scores
This is indicated by the model_results_dir

'''
import argparse
import pandas as pd

def map_prediction(value):
    return 1 if value == 1 else -1

if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-r", dest="results_directory", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-p", dest="prefix", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-i", dest="intermed_storage", required=True, help="Provide boolean to indicate if intermediate storage is required")
    
    # Read arguments from the command line
    args=parser.parse_args()

    # First we read in all the json formatted results

    embeddings = ['transformer' ,'doc2vec','tfid', 'bow_pos', 'bow_neg']
    models = ['adaboost','gradientboost','logistic_regression','randomforest']
    results={}
    for embed in embeddings:
        for mod in models:
            filename = args.results_directory + "/scores_" + mod + "_" + embed +".json"
            print("Processing " + filename)
            df = pd.read_json(filename, convert_axes=False).transpose().rename_axis("PMID").reset_index()
           
            #print(df)
#            df = pd.read_json(filename)
            
            df.columns = ['pmid','prediction', 'score', 'method']
            #print(df.head)
#            print(df)
            df['embedding'] = embed
            results[filename]=df
    
    # bow_models = ['bow_pos','bow_neg']
    
    # for bow in bow_models:
    #     filename = args.results_directory + "/scores_" + mod + "_" + bow +".json"
    #     print("Processing " + filename)
    #     df = pd.read_json(filename, convert_axes=False).transpose().rename_axis("PMID").reset_index()
        
    #     if bow == 'bow_neg':
    #         df.columns = ['pmid','neg_bow_prediction', 'neg_bow_score', 'method']
    #     else:
    #         df.columns = ['pmid','pos_bow_prediction', 'pos_bow_score', 'method']
    #     df['embedding'] = bow
    #     results[filename]=df
    
    df = pd.concat(results.values(), axis=0, ignore_index=True)
   

    # Apply the function to create the new column
    df['multiplier'] = df['prediction'].apply(map_prediction)
    # df['pos_bow_multiplier'] = df['pos_bow_prediction'].apply(map_prediction)
    # df['neg_bow_multiplier'] = df['neg_bow_prediction'].apply(map_prediction)
 
    #The score can now be calculated by multiplying the multiplier by the score
    df['pos_score'] = df.score * df.multiplier
    # df['pos_bow_score'] = df.pos_bow_score * df.pos_bow_multiplier
    # df['neg_bow_score'] = df.neg_bow_score * df.neg_bow_multiplier

    # Now we can calculate the average
    avg_scores = df.groupby(['pmid'])['pos_score'].agg(['mean', 'std'])
    # avg_pos_bow_scores = df.groupby(['pmid'])['pos_bow_score'].agg(['mean', 'std']).rename(columns={'mean':'mean_bow_pos', 'std':'std_bow_pos'})
    # avg_neg_bow_scores = df.groupby(['pmid'])['neg_bow_score'].agg(['mean', 'std']).rename(columns={'mean':'mean_bow_neg', 'std':'std_bow_neg'})
    nr_pos = df.groupby(['pmid'])['prediction'].agg(['sum'])
    # nr_bow_pos = df.groupby(['pmid'])['pos_bow_prediction'].agg(['sum']).rename(columns={'sum':'sum_bow_pos'})
    # nr_bow_neg = df.groupby(['pmid'])['neg_bow_prediction'].agg(['sum']).rename(columns={'sum':'sum_bow_neg'})
    
    df_merge = pd.merge(avg_scores, nr_pos, on='pmid')
    # df_merge = pd.merge(df_merge, avg_pos_bow_scores, on='pmid')
    # df_merge = pd.merge(df_merge, avg_neg_bow_scores, on='pmid')
    # df_merge = pd.merge(df_merge, nr_bow_pos, on='pmid')
    # df_merge = pd.merge(df_merge, nr_bow_neg, on='pmid')
    df_merge = df_merge.rename_axis("pmid").reset_index()  
    
    # Read JSON file with abstracts into a DataFrame
    df_abs = pd.read_json(args.results_directory + 'predict_pmids.json', convert_axes=False)
    #print(df_abs)
    df_merge['pmid'] = df_merge.pmid.astype(int)
    #print(df_merge)
    df_abs.pmid.astype(int)
    # Merge with the scores
    df_merge = pd.merge(df_merge , df_abs, on='pmid')

    if args.intermed_storage:
        df['pmid'] = df.pmid.astype(int)
        df = df.merge(df_abs, on='pmid')
        # Sort df by pos_score for intermediate storage but keep pmid order
        df = df.sort_values(by='pos_score', ascending=False)
        df = df.drop(columns=['multiplier', 'score'])
        df.rename(columns={'pos_score': 'score'}, inplace=True)
        
        # sort by pmid, method, embedding
        df = df.sort_values(by=['pmid', 'method', 'embedding'])
        
        df.to_excel(args.results_directory +'/'+args.prefix+ '_scored_overview.xlsx', index=False)

    # Sort on mean score
    df_merge = df_merge.sort_values(by ='mean')

    # Select top30 of each category
    df_tokeep =  pd.concat([df_merge.head(30), df_merge.tail(30)], ignore_index=True).sample(frac=1).reset_index(drop=True)
    
    df_merge.to_excel(args.results_directory +'/'+args.prefix+ '_merged_and_scored.xlsx', index=False)
    df_tokeep.drop(columns=["mean","std","sum"]).to_excel(args.results_directory +'/'+args.prefix+'_for_validation.xlsx', index=False)

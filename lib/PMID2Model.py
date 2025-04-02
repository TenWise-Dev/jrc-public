#!/usr/bin/env python

"""
This script loads a set of embeddings and uses the positive and negative PMIDs to create a dataset for training and validation.
This dataset is then used to train a set of classifiers and score them using cross validation and a test set.
The script has six required arguments. ::

    Required:
    
    -p : The path to the positive embeddings file
    -n : The path to the negative embeddings file
    -c : The path to the config JSON file
    -m : The path to the models folder
    -o : The path to the output file
    -ml : A list of models to load, comma separated
    
    Usage:
    
    python3 PMID2Model.py -p ../example/demo_pos_embeddings.npz -n ../example/demo_neg_embeddings.npz -c ../example/demo_config.json -m ../YOUR_FOLDER/models/ -o ../YOUR_FOLDER/results.csv -ml randomforest,adaboost

"""

# Import the required libraries
import argparse
import numpy as np
import pandas as pd
import json
import pickle

# Import various sklearn classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier

# Import model selection functions
from sklearn.model_selection import KFold, cross_validate, train_test_split

# Import scoring functions
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from tqdm import tqdm

def load_classifiers(config: dict, model_load: list) -> dict:
    # Make docstring with rst syntax
    """
    Load the classifiers from the config file.\n
    \n
    Parameters:\n
    - config: The config dictionary\n
    \n
    Returns:\n
    - classifiers: A dictionary of classifiers
    """
    
    included_classifiers = [model for model, include in config["models_include"].items() if include == True] 
    
    model_dict = {
        "lr": "logistic_regression",
        "rf": "randomforest",
        "gb": "gradientboost",
        "ab": "adaboost"
    }
                
    # Slice the classifiers if model_load argument is provided
    if args.model_load is not None:
        model_load = args.model_load.split(',')
        included_classifiers = [model for model in included_classifiers if model_dict[model] in model_load]
                
    classifiers = {}
    
    if "lr" in included_classifiers:
        classifiers["Logistic Regression"] = {
            "name" : "logistic_regression",
            "model" : LogisticRegression(
            **config["lr_params"]
            )
        }
    if "rf" in included_classifiers:
        classifiers["Random Forest"] = {
            "name" : "randomforest",
            "model" : RandomForestClassifier(
            **config["rf_params"]
            )
        }
    if "gb" in included_classifiers:
        classifiers["GradientBoost"] = {
            "name" : "gradientboost",
            "model" : GradientBoostingClassifier(
            **config["gb_params"]
            )        
        }
    if "ab" in included_classifiers:
        classifiers["AdaBoost"] = {
            "name" : "adaboost",
            "model" : AdaBoostClassifier(
            **config["ab_params"]
            )
        }
        
    return classifiers

def load_embeddings(embedding_file: str) -> np.ndarray:
    # Make docstring with rst syntax
    """
    Load the embeddings from a numpy npz file.\n
    \n
    Parameters:\n
    - embedding_file: The path to the embedding set .npz file\n
    \n
    Returns:\n
    - embeddings: The embeddings as a numpy array with the embeddings
    """
    
    embeddings = np.load(embedding_file)['embeddings']
    return embeddings

def make_datasets(
    pos_embeddings:     np.ndarray, 
    neg_embeddings:     np.ndarray, 
    test_size:          float = 0.2, 
    val_size:           float = 0.2, 
    random_state:       int =   42
    ) -> tuple:
    # Make docstring with rst syntax
    """
    Create a training, validation and test set from the embeddings and positive and negative PMIDs.\n
    \n
    Parameters:\n
    - pos_embeddings: The positive embeddings as a numpy array\n
    - neg_embeddings: The negative embeddings as a numpy array\n
    - test_size: The size of the test set\n
    - val_size: The size of the validation set\n
    - random_state: The random state for reproducibility\n
    \n
    Returns:\n
    - X_train: The training set embeddings\n
    - X_val: The validation set embeddings\n
    - X_test: The test set embeddings\n
    - y_train: The training set labels\n
    - y_val: The validation set labels\n
    - y_test: The test set labels
    """
       
    pos_features = pos_embeddings.astype(np.float32)
    neg_features = neg_embeddings.astype(np.float32)
    
    # Create a list of positive and negative labels
    pos_labels = [1] * len(pos_features)
    neg_labels = [0] * len(neg_features)
    
    # Concatenate the positive and negative embeddings and labels and make numpy arrays
    X = np.concatenate([pos_features, neg_features])
    y = np.concatenate([pos_labels, neg_labels])    
    
    # Split the data into training, validation and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y
        )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, 
        test_size=val_size, 
        random_state=random_state,
        stratify=y_train
        )

    return X_train, X_val, X_test, y_train, y_val, y_test

def cv_score(X: np.ndarray, y: np.ndarray, classifiers: dict) -> dict:
    # Make docstring with rst syntax
    """
    Score the classifiers using cross validation.\n
    \n
    Parameters:\n
    - X: The embeddings\n
    - y: The labels\n
    - classifiers: A dictionary of classifiers\n
    \n
    Returns:\n
    - results: A dictionary of scores
    """
    
    # Create a KFold object with 5 splits
    k_folds = KFold(n_splits = 5)
  
    # Create a dictionary to store the results
    results = {}
  
    print(f"Scoring {len(classifiers)} classifiers using CV")
  
    bar = tqdm(classifiers.items())
      
    # Fit the classifiers
    for name, classifier in bar:
        bar.set_description(f"CV Scoring {name}")
        model = classifier["model"]
        scores = cross_validate(model, X, y, cv = k_folds, return_train_score=True, n_jobs=-1, scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"])    
        results[name] = scores
            
    return results    

def fit_classifiers(X: np.ndarray, y: np.ndarray, classifiers: dict) -> dict:   
    # Make docstring with rst syntax
    """
    Fit the classifiers to the training set.\n
    \n
    Parameters:\n
    - X_train: The training set embeddings\n
    - y_train: The training set labels\n
    - classifiers: A dictionary of classifiers\n
    \n
    Returns:\n
    - classifiers: A dictionary of fitted classifiers
    """
        
    print(f"Fitting {len(classifiers)} classifiers to the test set scoring")
        
    bar = tqdm(classifiers.items())
    
    # Fit the classifiers
    for name, classifier in bar:
        bar.set_description(f"Fitting {name}")
        model = classifier["model"]
        model.fit(X, y)
        classifiers[name]['model'] = model
                
    return classifiers

def score_classifiers(classifiers: dict, X: np.ndarray, y: np.ndarray) -> dict:	
    # Make docstring with rst syntax
    """
    Score the classifiers on the given dataset.\n
    \n
    Parameters:\n
    - classifiers: A dictionary of fitted classifiers\n
    - X: The embeddings\n
    - y: The labels\n
    \n
    Returns:\n
    - scores: A dictionary of scores
    """
    # Create a dictionary to store the scores
    scores = {}
    
    # Score the classifiers
    for name, classifier in classifiers.items():
        model = classifier["model"]
        predictions = model.predict(X)
        results = {
            "Accuracy": accuracy_score(y, predictions),
            "Precision": precision_score(y, predictions),
            "Recall": recall_score(y, predictions),
            "F1": f1_score(y, predictions),
            "Roc_auc": roc_auc_score(y, predictions)
        }
        scores[name] = results
        
    return scores
    
def convert_scores(cv_scores: dict, test_scores: dict) -> pd.DataFrame:
    # Combine cv and test scores into a single DataFrame with multi-index
    # Create an empty list to collect the row data
    rows_list = []
    
    # Process CV scores for training and validation datasets
    for model, metrics in cv_scores.items():
        for dataset_type in ['train', 'test']: 
            dataset = 'val' if dataset_type == 'test' else 'train'
            row = {'Model': model, 'Dataset': dataset}
            for metric, values in metrics.items():
                if metric.startswith(dataset_type + '_'): 
                    metric_name = metric.split('_', 1)[1].capitalize()
                    row[metric_name] = round(np.mean(values), 2)
            rows_list.append(row)
            
    # Process Test scores
    for model, metrics in test_scores.items():
        row = {'Model': model, 'Dataset': 'test'}
        for metric, value in metrics.items():
            metric_name = metric  
            row[metric_name] = round(value, 2)
        rows_list.append(row)
    

    # Convert the list of dicts into a DataFrame
    full_scores_df = pd.DataFrame(rows_list)

    # Set multi-index (Model, Dataset) and sort for better readability
    full_scores_df.set_index(['Model', 'Dataset'], inplace=True)
    full_scores_df.sort_index(inplace=True)
    
    return full_scores_df
    
    
if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pos_file", required=True, help="Provide the path to the positive embeddings file")
    parser.add_argument("-n", dest="neg_file", required=True, help="Provide the path to the negative embeddings file")
    parser.add_argument("-c", dest="config_file", required=True, help="Provide the path to the config JSON file")
    parser.add_argument("-m", dest="models_folder", required=True, help="Provide the path to the models folder")
    parser.add_argument("-o", dest="output_file", required=False, help="Provide the path to the output file for saving the results")
    parser.add_argument("-ml", dest="model_load", required=False, help="A list of models to load, comma separated")

    # Read arguments from the command line
    args=parser.parse_args()
        
    # Load the config file
    with open(args.config_file, 'r') as file:
        config = json.load(file)
    
    classifiers = load_classifiers(config = config, model_load = args.model_load)
        
    # Read the embedding set
    pos_embeddings = load_embeddings(embedding_file=args.pos_file)
    neg_embeddings = load_embeddings(embedding_file=args.neg_file)
    
    # Create the datasets
    X_train, X_val, X_test, y_train, y_val, y_test = make_datasets(
        pos_embeddings=pos_embeddings, 
        neg_embeddings=neg_embeddings, 
        random_state=config["datasets"]["random_state"]
        )
    
    # Combine X_train and X_val and y_train and y_val for cross validation
    X = np.concatenate([X_train, X_val])
    y = np.concatenate([y_train, y_val])
    
    print("X_train shape:", X_train.shape)
    print("X_val shape:", X_val.shape)
    print("X_test shape:", X_test.shape)
    
    # Get cross validation scores
    cv_score_dict = cv_score(X, y, classifiers)
    
    print("---------------------------------------------------")
    
    # Train the classifiers 
    fitted_classifiers = fit_classifiers(X, y, classifiers)
    
    # Score the classifiers on the test set
    test_score_dict = score_classifiers(fitted_classifiers, X_test, y_test)
    
    # Convert all scores to one DataFrame
    df_scores = convert_scores(cv_scores = cv_score_dict, test_scores = test_score_dict)  
    
     
    # Print or save the scores
    print("---------------------------------------------------")
        
    # Check if output file argument is provided
    if args.output_file is not None:
        df_scores.to_csv(args.output_file, index=True)
        print(f"Results saved to {args.output_file}")
    else:
        print("Results:")
        print(df_scores)  
        
    # Check if models folder argument is provided
    if args.models_folder is not None:
        for classifier in fitted_classifiers.values():
            model_name = classifier["name"]
            model = classifier["model"]
            with open(f"{args.models_folder}/{model_name}.pkl", 'wb') as file:
                pickle.dump(model, file)
                
        print(f"Models saved to {args.models_folder}")
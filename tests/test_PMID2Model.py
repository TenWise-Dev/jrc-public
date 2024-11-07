import os
import sys
import json
import numpy as np
import pickle

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

input_pos = os.path.join(BASE_DIR, 'tests/data/example_pos_embeddings.npz')
input_neg = os.path.join(BASE_DIR, 'tests/data/example_neg_embeddings.npz')
config_file = os.path.join(BASE_DIR, 'tests/data/input_config.json')

output_file = os.path.join(BASE_DIR, 'tests/data/test_scores.npz')
example_file = os.path.join(BASE_DIR, 'tests/data/example_scores.npz')

models_folder = os.path.join(BASE_DIR, 'tests/data/models/')

# Make test for the function
def test_pmid2model():
    from lib.PMID2Model import load_classifiers, load_embeddings, make_datasets, cv_score, fit_classifiers, score_classifiers, convert_scores
    
    # Load the config file
    with open(config_file, 'r') as file:
        config = json.load(file)
    
    classifiers = load_classifiers(config = config)
    
    # Read the embedding set
    pos_embeddings = load_embeddings(input_pos)
    neg_embeddings = load_embeddings(input_neg)
    
    # Create the datasets
    X_train, X_val, X_test, y_train, y_val, y_test = make_datasets(
        pos_embeddings=pos_embeddings, 
        neg_embeddings=neg_embeddings, 
        random_state=config["datasets"]["random_state"]
        )
    
    # Combine X_train and X_val and y_train and y_val for cross validation
    X = np.concatenate([X_train, X_val])
    y = np.concatenate([y_train, y_val])
    
    # Get cross validation scores
    cv_score_dict = cv_score(X, y, classifiers)
    
    # Train the classifiers 
    fitted_classifiers = fit_classifiers(X, y, classifiers)
    
    # Score the classifiers on the test set
    test_score_dict = score_classifiers(fitted_classifiers, X_test, y_test)
    
    # Convert all scores to one DataFrame
    df_scores = convert_scores(cv_scores = cv_score_dict, test_scores = test_score_dict)  
    
    # Save the scores to a numpy file
    np.savez_compressed(output_file, scores=df_scores)
    
    output_scores = np.load(output_file)['scores']
    
    example_scores = np.load(example_file)['scores']
    
    # Check if dataframes have identical shape
    assert output_scores.shape == example_scores.shape
    
    # # Clean up
    os.remove(output_file)
    
    for classifier in fitted_classifiers.values():
        model_name = classifier["name"]
        model = classifier["model"]
        with open(f"{models_folder}/{model_name}.pkl", 'wb') as file:
            pickle.dump(model, file)

test_pmid2model()
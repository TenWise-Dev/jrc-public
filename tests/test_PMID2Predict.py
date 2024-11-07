import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

input_models = ["adaboost", "gradientboost", "logistic_regression", "randomforest"]

input_embedding = os.path.join(BASE_DIR, 'tests/data/example_pos_embeddings.npz')
output_file = os.path.join(BASE_DIR, 'tests/data/test_predictions.json')
example_file = os.path.join(BASE_DIR, 'tests/data/example_predictions.json')

# Make test for the function
def test_pmid2predict():
    from lib.PMID2Predict import load_embeddings, predict_embeddings
    
    # Retrieve embeddings from the CSV file
    embeddings = load_embeddings(embedding_file=input_embedding)
    with open(example_file, 'r') as file:
        example_data = json.load(file)
        
    for model in input_models:
        model_file = os.path.join(BASE_DIR, f'tests/data/models/{model}.pkl')
    
        # Predict the class of the embeddings using the provided model and save the results to a dictionary
        results = predict_embeddings(embeddings=embeddings, models_file=model_file)
        
        # Save the dictionary to a JSON file
        with open(output_file, 'w') as file:
            json.dump(results, file, indent=4)
        
        with open(output_file, 'r') as file:
            output_data = json.load(file)
            
        # Check if the output is the same as the example in terms of structure
        assert output_data.keys() == example_data.keys()
        
        # Clean up
        os.remove(output_file)
    
test_pmid2predict()
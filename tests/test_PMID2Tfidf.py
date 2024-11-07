import os
import sys
import numpy as np
from joblib import load

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

input_pmids = os.path.join(BASE_DIR, 'tests/data/input_pmids.txt')
database_file = os.path.join(BASE_DIR, 'tests/data/example_database.json')
pretrained_model_n2 = os.path.join(BASE_DIR, 'jrcdocs/downloads/tfidf-2.joblib')
pretrained_model_n3 = os.path.join(BASE_DIR, 'jrcdocs/downloads/tfidf-3.joblib')
output_file = os.path.join(BASE_DIR, 'tests/data/test_tfidf_embeddings.npz')

example_file = os.path.join(BASE_DIR, 'tests/data/example_tfidf_embeddings.npz')

from lib.PMID2Tfidf import fit_model, embed_abstracts, get_abstracts

def tfidf_checks(pretrained, model, pmid_abstracts, ngrams):
    if pretrained:
        model = load(model)
    else:
        model = fit_model(pmid_abstracts, n_ngrams=ngrams)
        
    abstracts_embedded, np_pmids = embed_abstracts(model=model, abstracts=pmid_abstracts)
    
    np.savez_compressed(output_file, embeddings=abstracts_embedded, keys=np_pmids)
    
    output_data = np.load(output_file)
    
    example_data = np.load(example_file)
            
    # Check if pmids are the same
    assert np.array_equal(output_data['keys'], example_data['keys'])
            
    # Check if the generated embedding dimensions are the same
    assert output_data['embeddings'].shape[0] == example_data['embeddings'].shape[0]
    
    # Clean up
    os.remove(output_file)
    
# Make test for the function
def test_pmid2tfidf():
    # Read the PMIDs from the txt files
    with open(input_pmids) as file:
        pmids = file.read().splitlines()
    
    # Read the database JSON file
    pmid_abstracts, _ = get_abstracts(pmids=pmids, database_file=database_file)
    
    options = [
    {
        'pretrained': True,
        'model': pretrained_model_n2,
        'pmid_abstracts': pmid_abstracts,
        'ngrams': 2
    },
    {
        'pretrained': True,
        'model': pretrained_model_n3,
        'pmid_abstracts': pmid_abstracts,
        'ngrams': 3
    },
    {
        'pretrained': False,
        'model': None,
        'pmid_abstracts': pmid_abstracts,
        'ngrams': 2
    },
    {
        'pretrained': False,
        'model': None,
        'pmid_abstracts': pmid_abstracts,
        'ngrams': 3
    }]
    
    for option in options:
        tfidf_checks(**option)
    
test_pmid2tfidf()
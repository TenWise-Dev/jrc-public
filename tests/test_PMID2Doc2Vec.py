import os
import sys
import numpy as np
from gensim.models.doc2vec import Doc2Vec

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

input_pmids = os.path.join(BASE_DIR, 'tests/data/input_pmids.txt')
database_file = os.path.join(BASE_DIR, 'tests/data/example_database.json')
pretrained_model = os.path.join(BASE_DIR, 'jrcdocs/downloads/doc2vec.model')
output_file = os.path.join(BASE_DIR, 'tests/data/test_d2v_embeddings.npz')

example_file = os.path.join(BASE_DIR, 'tests/data/example_doc2vec_embeddings.npz')

from lib.PMID2Doc2Vec import fit_model, embed_abstracts, get_abstracts

def check_d2v(pretrained, model, pmid_abstracts):
    if pretrained:
        model = Doc2Vec.load(model)
    else:
        model = fit_model(pmid_abstracts, n_epochs=40, n_workers=4)
        
    abstracts_embedded, np_pmids = embed_abstracts(model=model, abstracts=pmid_abstracts)
    
    np.savez_compressed(output_file, embeddings=abstracts_embedded, keys=np_pmids)
    
    output_data = np.load(output_file)
    
    example_data = np.load(example_file)
            
    # Check if pmids are the same
    assert np.array_equal(output_data['keys'], example_data['keys'])
            
    # Check if the generated embedding dimensions are the same
    assert output_data['embeddings'].shape == example_data['embeddings'].shape
    
    # Clean up
    os.remove(output_file)

# Make test for the function
def test_pmid2d2v():
    # Read the PMIDs from the txt files
    with open(input_pmids) as file:
        pmids = file.read().splitlines()
    
    # Read the database JSON file
    pmid_abstracts, _ = get_abstracts(pmids=pmids, database_file=database_file)
    
    options = [
        {
            'pretrained': True,
            'model': pretrained_model,
            'pmid_abstracts': pmid_abstracts
        },
        {
            'pretrained': False,
            'model': None,
            'pmid_abstracts': pmid_abstracts
        }
    ]
    
    for option in options:
        check_d2v(**option)
    
test_pmid2d2v()
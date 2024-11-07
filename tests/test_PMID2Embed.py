import os
import sys
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

pmid_file = os.path.join(BASE_DIR, 'tests/data/input_pmids.txt')
database_file = os.path.join(BASE_DIR, 'tests/data/example_database.json')
output_file = os.path.join(BASE_DIR, 'tests/data/test_pos_embeddings.npz')
example_file = os.path.join(BASE_DIR, 'tests/data/example_pos_embeddings.npz')

# Make test for the function
def test_pmid2embed():
    from lib.PMID2Embed import get_abstracts, load_model, embed_abstracts
    # Get all the PMIDs from the txt pmid file
    with open(pmid_file) as file:
        pmids = file.read().splitlines()
    
    # Read the database JSON files
    pmid_abstracts, _ = get_abstracts(pmids=pmids, database_file=database_file)
    
    model = load_model(model_name = 'all-MiniLM-L6-v2')
        
    # Call the function
    np_embedded, np_pmids = embed_abstracts(model=model, abstracts=pmid_abstracts)
    
    # Save the embeddings to a numpy file
    np.savez_compressed(output_file, embeddings=np_embedded, keys=np_pmids)
    
    output_data = np.load(output_file)
    
    example_data = np.load(example_file)
            
    # Check if pmids are the same
    assert np.array_equal(output_data['keys'], example_data['keys'])
            
    # Check if the generated embedding dimensions are the same
    assert output_data['embeddings'].shape[0] == example_data['embeddings'].shape[0]
    
    # Clean up
    os.remove(output_file)
    
test_pmid2embed()
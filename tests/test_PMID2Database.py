import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

pmid_file = os.path.join(BASE_DIR, 'tests/data/input_pmids.txt')
records_file = os.path.join(BASE_DIR, 'tests/data/test_records.txt')
output_file = os.path.join(BASE_DIR, 'tests/data/test_database.json')
example_file = os.path.join(BASE_DIR, 'tests/data/example_database.json')
example_records_file = os.path.join(BASE_DIR, 'tests/data/example_records.txt')
entrez_email = 'some@hotmail.nl'

# Make test for the function
def test_pmid2database():
    from lib.PMID2Database import get_records, parse_records, medline_to_json
    # Get all the PMIDs from the txt pmid file
    with open(pmid_file) as file:
        pmids = file.read().splitlines()
    
    # Get the records from the NCBI database
    get_records(pmids=pmids, outfile=records_file, entrez_email=entrez_email)
    
    with open(records_file, 'r') as file:
        records = file.read()
        
    with open(example_records_file, 'r') as file:
        example_records = file.read()
        
    assert records == example_records
    
    # Parse the records
    records = parse_records(file=records_file)
    
    # Parse the record output to enrich the JSON file
    medline_to_json(records=records, outfile=output_file)
    
    with open(output_file, 'r') as file:
        output_data = json.load(file)
        
    with open(example_file, 'r') as file:
        example_data = json.load(file)
            
    # Check if the output is the same as the example
    assert output_data == example_data
    
    # Clean up
    os.remove(output_file)
    os.remove(records_file)
    
test_pmid2database()
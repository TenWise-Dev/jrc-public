import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

json_file = os.path.join(BASE_DIR, 'tests/data/input_database_merge.json')
update_file = os.path.join(BASE_DIR, 'tests/data/example_tags.json')
output_file = os.path.join(BASE_DIR, 'tests/data/test_database_merge.json')
example_file = os.path.join(BASE_DIR, 'tests/data/example_database_merge.json')

# Make test for the function
def test_database_merge():
    from lib.DatabaseMerge import database_merge
    database_merge(json_file, update_file, output_file)
    
    with open(output_file, 'r') as file:
        output_data = json.load(file)
        
    with open(example_file, 'r') as file:
        example_data = json.load(file)
            
    # Check if the output is the same as the example
    assert output_data == example_data
    
    # Clean up
    os.remove(output_file)
    
test_database_merge()
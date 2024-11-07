import os
import sys
import ijson
import json

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(str(BASE_DIR))

input_file = os.path.join(BASE_DIR, 'tests/data/example_database.json')
input_keywords = os.path.join(BASE_DIR, 'tests/data/input_keyword_file.txt')
output_file = os.path.join(BASE_DIR, 'tests/data/test_tags.json')
example_file = os.path.join(BASE_DIR, 'tests/data/example_tags.json')

# Make test for the function
def test_pmid2tags():
    from lib.PMID2Tags import read_keyword_file, process_text
    
    category_dict = read_keyword_file(input_keywords)

    with open(input_file, 'rb') as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'item')
        result = {}
        # Iterate over the JSON objects
        for item in parser:
        # Process each JSON object as needed
            result[item['pmid']] = {"tagging_scores":process_text(text = item['abstract'], category_dict = category_dict)}
            
    # Write the updated data back to a JSON file  
    with open(output_file, 'w') as file:
        json.dump(result, file, indent=4)       
    
    with open(output_file, 'r') as file:
        output_data = json.load(file)
        
    with open(example_file, 'r') as file:
        example_data = json.load(file)
        
    # Check if the output is the same as the example
    assert output_data == example_data
    
    # Clean up
    os.remove(output_file)
    
test_pmid2tags()
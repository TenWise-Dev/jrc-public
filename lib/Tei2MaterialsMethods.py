'''
This script takes a folder with TEI files produced by Grobid and parses Materials and Methods section. ::

    Required:
    
    --tei_folder: Path to the folder with TEI files
    --output_folder: Path to the output folder

    Optional:
    -v : Be verbose
    
    Usage (from top level folder):
    
    python3 lib/Tei2MaterialsMethods.py --tei_folder example/fulltexts --output_folder example/materials_methods -v

'''
import argparse
import os 
import json
from bs4 import BeautifulSoup

def parse_tei_file(tei_file):
    ''' 
    Helper function that takes a path to a TEI file as an argument and returns its body.\n\n
    
    Parameters:\n
    - tei_file: The path to the TEI XML file.\n
    \n
    Returns:\n
    - Tag: BeautifulSoup object with the body of the TEI file.\n 
    '''
    with open(tei_file, 'r') as f:
        soup = BeautifulSoup(f, "lxml-xml")
        namespaces = {"TEI": "http://www.tei-c.org/ns/1.0"}
        return soup.select_one("TEI|body", namespaces=namespaces)

def extract_materials_methods(body, verbose) -> dict:
    ''' 
    Helper function that the BeautifulSoup Tag object with body and returns JSON representation
     of materials and methods sections. .\n\n
    
    Parameters:\n
    - body:  BeautifulSoup Tag object with the body of the TEI file.\n
    - verbose: If True, print verbose output.\n
    \n
    Returns:\n
    - dict: JSON representation of materials and methods sections.\n
    '''
    if verbose:
        print("Extracting 'Materials and Methods' section")
    
    materials_methods_level = None
    found_materials_methods = False
    result = {'Materials and Methods': []}
    
    namespaces = {"TEI": "http://www.tei-c.org/ns/1.0"}
    divs = body.select("TEI|div", namespaces=namespaces)

    for div in divs:
        head = div.select_one("TEI|head", namespaces=namespaces)
        if head is None:
            continue

        head_text = head.get_text().lower()
        current_level = None

        # Check if we're starting or continuing the 'Materials and Methods' section
        if 'materials' in head_text or 'methods' in head_text or found_materials_methods:
            if head_text == 'materials and methods': # First time in the section
                found_materials_methods = True
                materials_methods_level = current_level
            elif materials_methods_level is not None and current_level is not None and current_level <= materials_methods_level:
                break  # End of section by level comparison
            elif head_text in ['results', 'discussion', 'acknowledgements']:
                break  # End of section based on section name

            # Extract content of the div
            div_contents = [
                {child.name: child.get_text(strip=True)}
                for child in div.find_all(recursive=False) if child.name != 'head'
            ]
            
            section_header = f"h{current_level}" if current_level else "h"
            result['Materials and Methods'].append({"header": section_header, "title": head.get_text(), "content": div_contents})

    return result


def process_tei_files(tei_folder, output_folder, verbose) -> None:
    ''' 
    Function that processes all TEI files in a folder and writes the extracted materials and methods sections to JSON files.\n\n
    
    Parameters:\n
    - tei_folder: Path to the folder with TEI files.\n
    - output_folder: Path to the output folder.\n
    - verbose: If True, print verbose output.\n
    \n
    Returns:\n
    - None\n
    '''
    if verbose:
        print(f"Processing TEI files in {tei_folder}")
    tei_files = [f for f in os.listdir(tei_folder) if f.endswith('.tei.xml')]

    for file in tei_files:
        if verbose:
            print(f"Processing file: {file}")
        
        body = parse_tei_file(os.path.join(tei_folder, file))
        
        if body is None:
            if verbose:
                print(f"Warning: No body found in {file}")
            continue
        
        result = extract_materials_methods(body, verbose)
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f'{file.split(".grobid")[0]}.json')
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        
        if verbose:
            print(f"JSON content has been written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tei_folder", required=True, help="Provide the path to the folder with TEI files")
    parser.add_argument("--output_folder", required=True, help="Provide the path to the output folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    args = parser.parse_args()

    process_tei_files(args.tei_folder, args.output_folder, args.verbose)


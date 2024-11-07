#!/usr/bin/env python

'''
This script takes a folder with PDF files and uses GROBID to transform them into TEI files. ::

    Required:
    
    --folder: Path to the folder with PDF files
    --output_folder: Path to the output folder for TEI files

    Optional:
    --port: Port number for GROBID (default 8081)
    -v : Be verbose
    
    Usage (from top level folder):
    
    python3 lib/PDF2Tei.py --folder example/fulltexts --output_folder example/fulltexts -v

'''
import requests
import argparse
import os
from datetime import datetime

def PDF_to_TEI(pdf_files, verbose):
    '''
    Convert a list of PDF files to TEI XML files using GROBID service.\n
    \n
    Parameters:\n
    - pdf_files: List of PDF files to be converted to TEI XML\n
    - verbose: If True, print verbose output\n
    '''
    for file in pdf_files:
        input_json = {"input" : open(os.path.join(args.folder, file), "rb").read()}
        response = requests.post(base_url + 'processFulltextDocument', files=input_json)

        if response.status_code == 200:
            # We received a successful response, let's save the XML to a file
            xml_content = response.text

            # Specify the path where you want to save the file
            file_name = file.split('.pdf')[0]
            output_file_path = os.path.join(args.output_folder, f'{file_name}.grobid.tei.xml')

            # Writing the XML content to the file
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(xml_content)
            if verbose:
                print(f"Finished processing {file_name}. TEI content has been written to {output_file_path}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--folder", dest="folder", required=True, help="Provide the path to the folder with PDF files")
    parser.add_argument("--output_folder", dest="output_folder", required=True, help="Provide the path to the output folder with TEI files")
    parser.add_argument("--port", dest='port', required=False, default=8081, help="Provide the port number for GROBID")
    parser.add_argument("-v", dest="verbose", required=False, default=False, action="store_true", help="Be verbose")
    args=parser.parse_args()

    base_url = f'http://localhost:{args.port}/api/' # Assumes that GROBID is running on this URL

    # Find all PDF files in the input folder:
    pdf_files = [f for f in os.listdir(args.folder) if f.endswith('.pdf')]
    if args.verbose:
        print(f"{datetime.now().time().strftime('%H:%M:%S')} - Found {len(pdf_files)} PDF files in the folder. Processing...")
    PDF_to_TEI(pdf_files, verbose=args.verbose)
    if args.verbose:
        print("All PDF files have been processed.")
    


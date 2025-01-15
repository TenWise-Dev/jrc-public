#!/usr/bin/env python

'''
This script is used to load a list of PMIDs from a TXT file and enrich them with additional information from the NCBI database.
The information from the NCBI database is saved in a temporary file and then parsed a JSON file.
This JSON file then acts as a database.
The script has four required arguments. ::

    Required:
    
    -p : The path to the PMID file
    -j : The path to the output JSON file
    -r : The path to store the NCBI records file
    -e : The email address for the NCBI API
    
    Usage:
    
    python3 NewPMID.py -p ../example/demo_new_pmids.txt .j ../YOUR_FOLDER/demo_new_pmids.json -r ../YOUR_FOLDER/new_records_file.txt -e nielsvanbeuningen@gmail.com
    
'''

# Import the required libraries
from Bio import Entrez
from Bio import Medline
import json
import argparse
import time


def get_records(pmids: list, outfile: str, entrez_email: str) -> None:
    # Make docstring with rst syntax
    ''' 
    Takes a set of PMIDs and retrieves the records. Save the results to a temporary file.\n\n
    
    Parameters:\n
    - pmids: A list of PMIDs\n
    - outfile: The path to the output file\n
    - entrez_email: The email address for the NCBI API\n
    \n
    Returns:\n
    - None  
    '''

    # Batch size is the amount of records that are downloaded at once, to prevent overloading the server
    batch_size = 20

    Entrez.email = entrez_email
    
    # Concatenate the PMIDs to a string
    myterm = ",".join(pmids)
    
    # Get the search results
    search_results = Entrez.read(Entrez.esearch(
        db="pubmed",
        term=myterm,
        usehistory="y"
        ))
    
    # Count the amount of records for batch processing
    count = int(search_results["Count"])
    
    # Open the output file for saving the records
    out_handle = open(outfile, "w", encoding="UTF-8")
    
    # Loop over the records in batches
    for start in range(0, count, batch_size):
        end = min(count, start+batch_size)
        print("Going to download record %i to %i" % (start+1, end))
        
        # Fetch the records
        fetch_handle = Entrez.efetch(db="pubmed",
            rettype="medline",
            retmode="text",
            retstart=start,
            retmax=batch_size,
            webenv=search_results["WebEnv"],
            query_key=search_results["QueryKey"])

        data = fetch_handle.read()
        fetch_handle.close()
        
        # Save the records to the output file
        out_handle.write(data)
        
        # Sleep for 2 seconds to prevent overloading the server
        time.sleep(2)
    out_handle.close()
    
def parse_records(file: str) -> dict:   
    # Make docstring with rst syntax
    ''' 
    Takes a file with records and parses out the information.\n\n
    
    Parameters:\n
    - file: The path to the file with records\n
    \n
    Returns:\n
    - record_dict: A dictionary with the records
    '''

    # Open the file with records
    with open(file) as handle:
        # Parse the records using the Medline parser
        records = Medline.parse(handle)

        # Create a dictionary to store the records
        record_dict = {}
        for rec in records:
            record_dict[rec.get('PMID')]=rec
    return record_dict

def medline_to_json(records: dict, outfile: str) -> None:
    # Make docstring with rst syntax
    """
    Parse the record output file to enrich a JSON-structured output file with the information from the NCBI database used to update a main database file.\n
    The file is structured as:\n
    \n
    .. code-block:: json
    
        {
            "PMID1": {
                "doi": "DOI1",
                "title": "TITLE1"
                },
            "PMID2": {
                "doi": "DOI2",
                "title": "TITLE2"
                }
        }
    \n
    Parameters:\n
    - records: A dictionary with the records\n
    - outfile: The path to the output JSON file\n
    \n
    Returns:\n
    - None
    """
    
    output_list = {}
    
    # Loop over the records
    for pmid in records:
        record = records[pmid]
        
         # Get the authors if the information is available
        if record.get('FAU') is not None:
            authors =" and ".join([au for au in record.get('FAU')])
            first_author = record.get('FAU')[0]
        else:
            authors = ""
            first_author = ""
            
        if record.get('MH') is not None:
            mesh =";".join([mh for mh in record.get('MH')])
        else:
            mesh = ""

        if record.get('RN') is not None:
            substances =";".join([rn for rn in record.get('RN')])
        else:
            substances = ""
            
        if record.get('PT') is not None:
            article_type ="; ".join([pt for pt in record.get('PT')])
        else:
            article_type = ""    
            
        doi = ""

        # Retrieve DOI if available
        if record.get('AID') is not None and any(aid.startswith('10.') for aid in record.get('AID')):
            # Get the DOI from the list of AID's, slice the first DOI and remove the '[doi]' tag
            doi = [aid for aid in record.get('AID') if aid.startswith('10.') and aid.endswith('[doi]')]
            if len(doi) > 0:
                doi = doi[0]
            else:
                doi = ""
            
        # Create a dictionary with the information to be added to the JSON file
        output_list[pmid] = {
            "doi":doi,
            "author":authors, 
            "first_author":first_author,
            "title":record.get('TI'), 
            "year":record.get('DP'), 
            "journal":record.get('JT'), 
            "volume":record.get('VI'), 
            "issue":record.get('IP'), 
            "article_type":article_type,
            "pages":record.get('PG'), 
            "abstract":record.get('AB'),
            "issn":record.get('IS'),
            "mesh":mesh,
            "substances":substances
            }
              
    # Write the updated data back to the JSON file  
    with open(outfile, 'w') as file:
        json.dump(output_list, file, indent=4)
    
if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pmid_file", required=True, help="Provide the path to the PMID file")
    parser.add_argument("-j", dest="json_file", required=True, help="Provide the path to the Output JSON file")
    parser.add_argument("-r", dest="records_file", required=True, help="Provide the path to store the NCBI records file")
    parser.add_argument("-e", dest="entrez_email", required=True, help="Provide the email address for the NCBI API")

    # Read arguments from the command line
    args=parser.parse_args()
    
    # Get all the PMIDs from the txt pmid file
    with open(args.pmid_file) as file:
        pmids = file.read().splitlines()
       
    # Get the records from the NCBI database
    get_records(pmids=pmids, outfile=args.records_file, entrez_email=args.entrez_email)
    
    # Parse the records
    records = parse_records(file=args.records_file)
    
    # Parse the record output to enrich the JSON file
    medline_to_json(records=records, outfile=args.json_file)
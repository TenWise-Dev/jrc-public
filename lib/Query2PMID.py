#!/usr/bin/env python

'''

This script executes a set of queries that are supplied in an Excel file. For each query, a result file is created in the output directory specified by the -o option. The result file is named after the query_id that is specified in the first column of the Excel file.

The script has three required arguments. ::

    Required:
    
    -q : The path to the Excel file with the queries
    -o : The path to the output directory    
    -e : The email address for the NCBI API
    
    Usage:
    
    ./Query2PMID.py -q ../example/example_query.xlsx -o /tmp/  -e youremail@email.com
    
'''

# Import the required libraries
from Bio import Entrez
from Bio import Medline
import sys
from openpyxl import load_workbook
import argparse
import time


    
if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-q", dest="query_file", required=True, help="An Excel file with queries")
    parser.add_argument("-o", dest="output_directory", required=True, help="Provide the path to the Output JSON file")
    parser.add_argument("-e", dest="entrez_email", required=True, help="Provide the email address for the NCBI API")

    # Read arguments from the command line
    args=parser.parse_args()

    # Load the Excel file
    workbook = load_workbook(args.query_file)

   
    # Select the active sheet or specify a sheet by name
    sheet = workbook.active

    # Iterate through rows in the sheet
    queries = {}
    for row in sheet.iter_rows(min_row=2,values_only=True):
        full_query = row[1]
        # Add the query to the dictionary with row[0] as the key (disease area)
        queries[row[0]] = full_query


       
    Entrez.email = args.entrez_email

    for q in queries.keys():
        print("Running query " + queries[q])
        OUT = open(args.output_directory+"/"+q+"_predict_pmids.txt","w")
        handle = Entrez.esearch(db="pubmed", retmax=2500, term=queries[q])
        record = Entrez.read(handle)
        handle.close()
        OUT.write("\n".join(str(x) for x in (record['IdList'])))
        OUT.close()
        time.sleep(2)

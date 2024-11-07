Building the database
======================

This workflow describes the creation or update of an existing database based on a list of PubMed identifiers (PMIDs). The PMIDs are provided as a flatfile with one PMID per line. These PMID can be retrieved from a query to PubMed or can be obtained from a screening exercise. A typical list of PMIDs looks like this: ::

    26285657
    25323824
    28506444
    26549107
    27396853
    27637760
    29420117
    29420117
    29550474
    26015947


This file with PMIDs is used to query the NCBI for additional bibliographic information. To make sure we are up to date, we use the **entrez** module in Python to connect to the NCBI database. 

A typical usage of this script (assuming your are in the lib directory) is ::

     python3 pmid_enrichment.py \
     -p ../example/demo_pmids.txt \
     -j ../example/demo_pmids.json \
     -e jon.doe@gmail.com \
     -r ../example/pmid_records.txt

Running this script results in a json formatted file with a large number of entries. An example of the json output can be found in the examples directory.




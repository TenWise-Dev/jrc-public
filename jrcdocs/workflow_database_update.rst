Database update
===============

This workflow describes the update of the JSON formatted database with new data for existing PMIDs. The first step is the generation of new data for the PMIDs with an external script or from an external database that contains data on these PMIDs. In this workflow we will use the Python script :ref:`my-tagabstracts-label` to generate additional data for the current database. ::

    python3 tag_abstracts.py \
        -j ../example/demo_pmids.json \
        -k ../example/keyword_file.txt \
        -o ../example/tagged_abstracts.json 
        

This will result in a file with tagging results for each PMID. An excerpt of this file is shown below and can be found in the example download directory ::

    },
    "30617277": {
        "tagging_scores": {
            "organoid": {
                "organoid": 0,
                "organ-on-a-chip": 0
            },
            "cells": {
                "ipsc": 3
            },
            "vitro": {
                "in-vitro": 0,
                "ELISA": 0
            }
        }
    },
    "30095002": {
        "tagging_scores": {
        ........

Next we need to merge these results with the existing database, stored in the JSON formatted database. This accomplished with the :ref:`my-databasemerge-label` script. This is done as follows ::

    python3 database_merge.py \
        -j ../example/demo_pmids.json \
        -u ../example/tagged_abstracts.json \
        -o ../example/merged_json.json

This yields a final merged json file in which the tagging scores have been added. 



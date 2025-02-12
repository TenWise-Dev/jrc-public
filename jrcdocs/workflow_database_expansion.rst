Database creation
=================

This workflow describes the update of the JSON formatted database with new PMIDs with a query that is run on the the most recent part of the MEDLINE database. The workflow exists of the following components:

 1. Execute the query on the MEDLINE database
 2. Retrieve the abstracts and create a JSON file from the abstracts.
 3. Enrich the JSON files with additional metadata
    - openAlex identifiers
    - tagging with controlled vocabularies
 4. Aggregating the data 
 5. Merging the database to the existing database  

Executing the query
-------------------

This steps reads one or more queries from an Exel file. The format of the file is shown in the figure below. 

.. image:: /images/query_file.png

The  :ref:`my-query2pmid-label` script executes the queries at real time on the MEDLINE database. ::
    
   workdir=/tmp/examplejrc/
   mkdir $workdir

   
    ./Query2PMID.py \
    -q ../example/example_query.xlsx \
    -o $workdir \
    -r 100  \
    -e youremail@email.com
 
   ls -ltrh $workdir

This results in pmid files in the workdir ::

    example_query_predict_pmids.txt  
    organoid_query_predict_pmids.txt


Retrieving the abstracts
------------------------

In the next steps, the abstracts for the PMIDs are retrieved using the :ref:`my-pmid2database-label` script. This may take a while dependent on the number of abstracts that you want to retrieve. In this example we use a nuber of 10 pmids to illustrate the idea. ::

    head -10 $workdir/organoid_query_predict_pmids.txt > $workdir/tmp_pmids.txt

    ./PMID2Database.py \
    -p $workdir/tmp_pmids.txt \
    -j $workdir/tmp_json.txt \
    -r $workdir/tmp_rec.txt \
    -e youremail@email.com

    more $workdir/tmp_json.txt

which yields ::

    [
    {
        "pmid": "39468757",
        "doi": "10.1093/stcltm/szae078 [doi]",
        "author": "Lim, Diana and Kim, Ickhee and Song, Qianqian and Kim, Ji Hyun and Atala, Anthony and Jackson, John D and Yoo, James J",
        "first_author": "Lim, Diana",
        "title": "Development and intra-renal delivery of renal progenitor organoids for effective integration in vivo.",
        "year": "2024 Oct 28",
        "journal": "Stem cells translational medicine",
        "volume": null,
        "issue": null,
        "article_type": "Journal Article",
        "pages": null,
        "abstract": "Renal progenitor organoids have been proposed as a source of tissue for kidney regeneration; however, their clinical translatability has not been demonstrated due to an inability to mass-produce comprehensive renal progenitor organoids and the lack of an effective intra-renal delivery platform that facilitates rapid integration into functionally meaningful sites. This study addresses these shortcomings. Human-induced pluripotent stem cells were differentiated into renal progenitor cells using an established protocol and aggregated using a novel assembly method to produce high yields of organoids. Organoids were encapsulated in collagen-based scaffolds for in vitro study and in vivo implantation into mouse renal cortex.In vitro, the organoids demonstrated sustained cell viability and renal structure maturation over time. In vivo delivered organoids showed rapid integration into host renal parenchyma while showing tubular and glomerular-like structure development and maturity markers. This proof-of-concept study presents many promising results, providing a system of renal organoid formation and delivery that may support the development of clinically translatable therapies and the advancement of in vitro renal organoid studies.",
        "issn": "2157-6580 (Electronic) 2157-6564 (Linking)",
        "mesh": "",
        "substances": ""
    },
    {
        "pmid": "39468028",
    ......    



Enriching the abstracts
-----------------------

The next step is to enrich the abstracts with additional metadata. We have two sources that are important. The first one ar ea number of identifiers that link the PMIDs to other identifiers related to open source availability.

OpenAlex
########

This is an R script, because we make use of an open source code library that is only available in R (to our knowledge) ::

    ./PMID2Openalex.R \
    -p $workdir/tmp_pmids.txt \
    -o $workdir/openalex.json \
    -e your_email@email.com

    more $workdir/openalex.json

which yields ::

    {
    "39462675": {
    "pmid": "39462675",
    "openalex_id": "W4403850379",
    "pmcid": "",
    "doi": "10.7507/1001-5515.202404036",
    "cited_by_count": 0,
    "pdf_url": null,
    "is_oa": false,
    "is_oa_anywhere": false
    },
    "39463945": {
    "pmid": "39463945",
    "openalex_id": "W4403385606",
    "pmcid": "",
    "doi": "10.1101/2024.10.13.617729",
    "cited_by_count": 2,
    "pdf_url": "https://www.biorxiv.org/content/biorxiv/early/2024/10/14/2024.10.13.617729.full.pdf",
    "is_oa": true,
    "is_oa_anywhere": true
    },



Keyword tagging
###############

The next source of meta information is tagging with the keywords that denote the disease and or experimental technique that is being described in the abstract. For this we use the :ref:`my-pmid2tags-label` script. ::

    ./PMID2Tags.py \
    -j $workdir/tmp_json.txt \
    -k ../data/keywords_for_tagging_2024_12_15.txt \
    -o $workdir/tagged_abstracts_json.txt





Aggregating the data
--------------------

The created JSON files can now be added together ::

    ./DatabaseMerge.py \
    -j $workdir/tmp_json.txt \
    -u $workdir/openalex.json \
    -o $workdir/first_database_merge.json

    ./DatabaseMerge.py \
    -j $workdir/first_database_merge.json \
    -u $workdir/tagged_abstracts_json.txt \
    -o $workdir/new_database_complete.json

    more $workdir/new_database_complete.json

Which yields ::

       {
        "pmid": "39464086",
        "doi": "10.1101/2024.10.04.614143",
        "author": "East, Michael P and Sprung... Gary L",
        "first_author": "East, Michael P",
        "title": "Quantitative proteomic mass spectrometry of protein kinases to determine dynamic heterogeneity of the human kinome.",
        "year": "2024 Oct 4",
        "journal": "bioRxiv : the preprint server for biology",
        "volume": null,
        "issue": null,
        "article_type": "Journal Article; Preprint",
        "pages": null,
        "abstract": "The kinome is a dynamic ....
                     ....... with nanoscale phosphoproteomics, providing a feasible method for novel clinical diagnosis and understanding of patient kinome responses to treatment.",
        "issn": "2692-8205 (Electronic) 2692-8205 (Linking)",
        "mesh": "",
        "substances": "",
        "openalex_id": "W4403116615",
        "pmcid": "",
        "cited_by_count": 0,
        "pdf_url": null,
        "is_oa": false,
        "is_oa_anywhere": false,
        "tagging_scores": {
            "human_anatomy": {
                "Breast": 2,
                "Organoids": 1,
                "Tissues": 2
            },
            "In_Silico": {},
            "In_Vitro": {
                "cell line": 1,
                "Organoid": 1
            },
            "In_Chemico": {},
            "General": {},
            "In_vitro": {},
            "Epigenomic": {},
            "Genomic": {},
            "Metabolomic": {
                "LC MS": 1
            },
            "Proteomic": {},
            "Transcriptomic": {}
        }
    },
    .......


Merging the database with an existing database
-----------------------------------------------

This database can be merged with an existing JSON formatted database. The typical scenario is that you have an existing database with articles and you want to add new articles to that database. Probably you want to add the new database after some curation and possibly selection based on the model scores.

Suppose the first database is created like this ::

    head -10 $workdir/organoid_query_predict_pmids.txt > $workdir/tmp_pmids.txt 
    ./PMID2Database.py -p $workdir/tmp_pmids.txt -j $workdir/first_json.txt -r $workdir/tmp_rec.txt -e  youremail@email.com

    tail -10 $workdir/organoid_query_predict_pmids.txt > $workdir/tmp_pmids.txt 
    ./PMID2Database.py -p $workdir/tmp_pmids.txt -j $workdir/second_json.txt -r $workdir/tmp_rec.txt -e  youremail@email.com

The merging can now easily be achieved by invoking the jq command ::

     jq -s '.[0] + .[1]' $workdir/first_json.txt $workdir/second_json.txt > $workdir/full_db.json

     grep "pmid" $workdir/full_db.json 

This should give 20 pmids::
  
    "pmid": "39468757",
    "pmid": "39468028",
    "pmid": "39465429",
    "pmid": "39464086",
    "pmid": "39464076",
    "pmid": "39464073",
    "pmid": "39464051",
    "pmid": "39463990",
    "pmid": "39463945",
    "pmid": "39462675",
    "pmid": "37166371",
    "pmid": "37164272",
    "pmid": "36958586",
    "pmid": "36909636",
    "pmid": "36815360",
    "pmid": "36722705",
    "pmid": "36515896",
    "pmid": "36302966",
    "pmid": "35984017",
    "pmid": "35864023",




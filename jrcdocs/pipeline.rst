Pipeline
========

The current thinking of the entire production pipeline (Using the word NAM here for human based biomedical model) is as follows:


 - Query the MEDLINE Database
 We begin by running a targeted query on PubMed to retrieve articles related to NAMs. 

 - Embedding and Classifying Articles
 Each article is embedded and classified using four different classification models combined with three embedding techniques. 

 - Expert Rule-Based Scoring with Positive BagofWords (BOW)
 To strengthen the classification, we apply an expert rule-based system that uses a curated list of positive keywords specific to NAMs. This is an additional step to further prioritise high scoring articles.

 - Expert Rule-Based Scoring with Negative Keywords in the title (Title2flags script)
 To minimize false positives, we apply a second scoring system using expert-curated negative keywords on the title of the articles. This is still under evaluation. This step helps eliminate articles that are clearly about animal models (such as knock-out mice, rat models etc.).
 
 -  Final List of NAM Articles
 Based on the outputs of steps 1–4 a final list of NAM-related articles can be produced. This should be done by applying a threshold to each individual classifier-embedding combination. This threshold is still under evaluation, because it depends on the final user requirements.
 
 - Enriching Articles with Bibliographic Information
 Once the final set of NAM articles is selected, each article will be enriched with bibliographic metadata, including author details, journal information, publication date, and relevant Medical Subject Headings (MeSH) terms.
 
 - Retrieving Full Text from Open Access Papers
 For articles linked to open-access papers, the full text is retrieved and Materials and Methods is extracted.
 
 - Tagging Articles with Vocabularies
 The title, abstracts and parts of the full text will be tagged using domain-specific vocabularies, such as keywords related to human anatomy, omics techniques, and models.
 
 - Creating an Integrated JSON File
 All collected and enriched data are compiled into a structured JSON file. This file will integrate title,abstracts, bibliographic metadata, keyword tags. Full text tagged content maybe large and can be stored in a separate file assuring the PMID identifier is the same!
 
 - Running ElasticSearch on the JSON Data
 The JSON file will be indexd using ElasticSearch, enabling querying of the NAM articles by other keywords.

 - Displaying Results in the Web Application
 The data will be searchable both by the Elastic Search Index as well as with the tagging results in the interactive web application.

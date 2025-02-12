.. warning::

    Since we are still working on this project and designing the best workflows, the scripts and their associated command line parameters are subject to change. However we expect that the overall functionality of the scripts will not change significantly and we will make sure that all additional options to scripts will be optional (wherever possible), minimising the chance of breaking pipeline code. So they can be used already, but production level workflows should be tested on the latest versions of these scripts. Make sure to have these tests for your specific workflow in place.


Scripts
=======

The scripts are supplied as standalone files, not as a packaged library. Most scripts take arguments for input and output files as command line arguments and can thus be used to redirect and retrieve data according to the specific directory set-up of your system. 


Database handling
#################

A set of scripts that deals with creation and updating the JSON formatted database. 

.. _my-query2pmid-label:

Query2PMID
----------

.. automodule:: Query2PMID



DOI2PMID.R
----------

An Rscript to interact with OpenAlex ::

    #!/usr/bin/env Rscript 

    library(openalexR)
    library(tidyr)
    library(jsonlite)
    library(stringr)
    library(dplyr)
    library(argparse)

    dois_to_pmids <- function(dois = NULL, your_email = NULL, output_file = NULL) {
        #' Function to retrieve PMIDs from OpenAlex for a list of DOIs and save it to a tab-delimited file
        #' @param dois List of dois
        #' @param your_email Email address for OpenAlex
        #' @param output_file Path to output file
        #' @return pmids List of PMIDs
        
        works_from_dois <- oa_fetch(
        entity = "works",
        doi = dois,
        verbose = TRUE
        )

        if (is.null(works_from_dois)) {
        return("No results found")
        }

        results <- works_from_dois %>% 
        rowwise() %>% 
        mutate(pmid = ifelse("pmid" %in% names(ids), ids[["pmid"]], "Not found")) %>%
        mutate(pmid = gsub(pmid, pattern="https://pubmed.ncbi.nlm.nih.gov/", replace="")) %>% 
        pull(pmid)

        return(results)
    }


    # create parser object
    parser <- ArgumentParser()
    parser$add_argument("-e", dest="email", required=TRUE, help="Email address for OpenAlex")

    args <- parser$parse_args()

    # Read data from stdin
    doi_source <- readLines(con = "stdin")

    # Check if email argument is given
    if (is.null(args$email)){
    stop("Please provide an email address for OpenAlex")
    }

    # Run the function
    pmids <- dois_to_pmids(dois = doi_source, your_email = args$email)

    cat(pmids, sep="\n")




.. _my-pmid2database-label:

PMID2Database
-------------

.. automodule:: PMID2Database



.. _my-openalex-label:

PMID2Openalex
-------------

An R script used for the retrieval of OpenAlex identifiers ::

    #!/usr/bin/env Rscript 

    library(openalexR)
    library(tidyr)
    library(jsonlite)
    library(dplyr)
    library(argparse)

    # Cite the package
    citation("openalexR")

    pmid_enrichment <- function(pmid_file = NULL, your_email = NULL, output_file = NULL){
    #' Function to retrieve information from OpenAlex for a list of PMIDs and save it to a JSON file
    #' @param pmid_file Path to file with PMIDs on each line
    #' @param your_email Email address for OpenAlex
    #' @param output_file Path to output file
    #' @return None
    
    # Load the PMIDs from the txt file
    pmids <- read.delim(pmid_file, header = F, sep = "\n") %>% pull(V1) %>% unique()

    # Enter polite pool with email
    if (!is.null(your_email)){
        options(openalexR.mailto = your_email)
    }

    # Function for information retrieval using OpenAlex
    get_oa_frame <- function(pmids){
        works_from_pmids <- oa_fetch(
        entity = "works",
        pmid = pmids,
        verbose = TRUE
        )
        return(works_from_pmids)
    }

    # Retrieve records using OpenAlex
    tp <- get_oa_frame(pmids = pmids)
    
    # Mutate dataframe in nice format
    idframe <- bind_rows(tp$ids) 
    # Some identifier types may not be present
    if (!"pmcid" %in% names(idframe)){
        idframe<- idframe %>% mutate(pmcid = "")
    }
    
    idframe <- idframe %>% 
        mutate(
        pmid = gsub(pmid, pattern=".*/", replace=""),
        oa_pmicd = gsub(pmcid, pattern=".*/", replace=""),
        doi = gsub(doi, pattern="https://doi.org/", replace=""),
        openalex_id = gsub(openalex, pattern=".*/", replace="")
        ) 

        fullframe <- idframe %>% 
        inner_join(tp, by = c("openalex"="id")) %>%
        rename(doi = doi.x)

        results <- fullframe %>% 
        select(pmid, openalex_id, oa_pmicd, doi, cited_by_count, pdf_url,is_oa,is_oa_anywhere)

        # Convert to named list with pmid as key
        results_split <- split(results, results$pmid)

        # Convert tibbles to lists
        results_list <- lapply(results_split, function(x) as.list(x %>% slice(1)))

        # Convert the list to JSON
        results_json <- toJSON(results_list, pretty = TRUE, auto_unbox = TRUE)

        # Save results to json file
        write(results_json, file = output_file)
    }

    # create parser object
    parser <- ArgumentParser()
    parser$add_argument("-p", dest="pmid_file", required=TRUE, help="Path to file with PMIDs on each line")
    parser$add_argument("-e", dest="email", required=TRUE, help="Email address for OpenAlex")
    parser$add_argument("-o", dest="output_file", required=TRUE, help="Path to output JSON file")

    args <- parser$parse_args()

    # Check if pmid file argument is given
    if (is.null(args$pmid_file)){
    stop("Please provide a path to a file with PMIDs on each line")
    }

    # Check if output file argument is given
    if (is.null(args$output_file)){
    stop("Please provide a path to an output_folder")
    }

    # Check if email argument is given
    if (is.null(args$email)){
    stop("Please provide an email address for OpenAlex")
    }

    # Run the function
    pmid_enrichment(pmid_file = args$pmid_file, your_email = args$email, output_file = args$output_file)




.. _my-pmid2tags-label:

PMID2Tags
---------

.. automodule:: PMID2Tags


.. _my-databasemerge-label:

DatabaseMerge.py
----------------

.. automodule:: DatabaseMerge


Database2PDF
------------

.. automodule:: Database2PDF

PDF2Tei
--------

.. automodule:: PDF2Tei

Tei2MaterialsMethods
--------------------

.. automodule:: Tei2MaterialsMethods
                
Excel2Keywords
--------------

.. automodule:: Excel2Keywords



DatabaseValidation
------------------

.. automodule:: DatabaseValidation    

Modelling
#########

A set of scripts that deals with creation of predictive models.

PMID2Embed.py
-------------

.. automodule:: PMID2Embed

PMID2Tfidf.py
-------------    

.. automodule:: PMID2Tfidf  


PMID2Doc2Vec.py
---------------

.. automodule:: PMID2Doc2Vec

.. _my-tagabstracts-label:


PMID2BOW.py
-----------

.. automodule:: PMID2BOW


Title2Flags
-----------

.. automodule:: Title2Flags


PMID2Predict.py
---------------

.. automodule:: PMID2Predict

PMID2Model.py
-------------

.. automodule:: PMID2Model
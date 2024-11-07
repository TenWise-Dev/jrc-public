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
      pmcid = gsub(pmcid, pattern=".*/", replace=""),
      doi = gsub(doi, pattern="https://doi.org/", replace=""),
      openalex_id = gsub(openalex, pattern=".*/", replace="")
    ) 

    fullframe <- idframe %>% 
      inner_join(tp, by = c("openalex"="id")) %>%
      rename(doi = doi.x)

    results <- fullframe %>% 
      select(pmid, openalex_id, pmcid, doi, cited_by_count, pdf_url,is_oa,is_oa_anywhere)

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
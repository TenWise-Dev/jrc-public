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

# Split doi and source and keep second column
dois <- lapply(strsplit(doi_source, "\t"), function(x) x[[1]]) %>% unlist()

# Check if email argument is given
if (is.null(args$email)){
  stop("Please provide an email address for OpenAlex")
}

# Run the function
pmids <- dois_to_pmids(dois = dois, your_email = args$email)

print(pmids)
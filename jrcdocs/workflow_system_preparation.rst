System prerequisites
====================

This document describes the system requirements for creating the database, developping and testing the models and creating regular updates.


Operating system
----------------

All scripts were developed and tested on a standard Ubuntu 22.04 system. The core of the system is formed by a set of Python scripts, but also helper utilities were written in R and bash shell scripts. These scripts are covered in more detail below, and individal scripts are extensively documented and can be accessed in the Scripts section of this documentation.


File system set-up
------------------

The framework is build with a number of scripts and a number of supporting data files to test the scripts and to provide examples. The directory structure is shown below ::
    
    .
    ├── classifier_models
    ├── data
    ├── embedding_models
    ├── example
    ├── jrcdocs
    ├── lib
    ├── requirements.txt
    ├── tests
    └── validation_template

classifier_models
#################

This directory contains the final models that are used for clasification.

data
####

This directory contains a number of data files that can be used to build the database. It also contains a number of Excel files that contain the results of the manula validations.

embedding_models
################

This directory contains the embedding files that are needed for embedding new abstracts and subsequently running the predictions.

example
#######

A directory with a number of example files that can be used for testing the system. Example files contain files with PMIDS, predefined embeddings, full text PDFS etc. Most of these file are needed to reproduce the **usage** examples in the Python and R scripts.

jrcdocs
#######
This contains the *.rst* file that are used to create the documentation (i.e. what you are reading now).

lib
###
The directory with all the Pyhton, shell and R scripts that are need to run the framework.

test
####
A set of test scipts meant to be used by developers. It contains unittests to check for broken scripts after addition of new code or modification of existing code.

validation_template
###################
A set of emtpy directories that can be copied as a working directory and can be used for developing and validating new and/or updated models.

requirements.txt
#################

A set of Python modules that is needed for this framework. Can typically be installed with ::

    pip install -r requirements.txt

The current requirements are ::

    ijson==3.2.3
    pandas==2.2.1
    numpy==1.26.4
    joblib==1.3.2
    biopython==1.83
    scipy==1.12.0
    sentence-transformers==2.5.1
    scikit-learn==1.4.1.post1
    torch==2.2.1
    tokenizers==0.15.2
    gensim==4.3.2
    nltk==3.8.1
    pytest==8.1.1
    openpyxl==3.1.2
    beautifulsoup4==4.12.0



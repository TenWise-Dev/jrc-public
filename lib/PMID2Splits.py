#!/usr/bin/env python

"""
This script loads a set of PMIDs from two files and splits them into training and testing sets.
The script saves the training and testing sets as txt files in the output folder.
The script has five required arguments. ::

    Required:
    
    -p : The path to the positive pmid file
    -n : The path to the negative pmid file
    -o : The path to the output folder
    
    Usage:
    
    python3 PMID2Splits.py -p ../example/pos_pmids.txt -n ../example/neg_pmids.txt -o ../example/

"""

# Import the required libraries
import argparse
import numpy as np

# Import model selection functions
from sklearn.model_selection import train_test_split

def make_datasets(
    pos_pmids:     np.ndarray, 
    neg_pmids:     np.ndarray, 
    split_size:         float = 0.2, 
    random_state:       int =   42
    ) -> tuple:
    # Make docstring with rst syntax
    """
    Create a training, validation and test set from the positive and negative PMIDs.\n
    \n
    Parameters:\n
    - pos_pmids: The positive PMIDs\n
    - neg_pmids: The negative PMIDs\n
    - split_size: The size of the test set\n
    - random_state: The random state for the split\n
    \n
    Returns:\n
    - pos_pmids_train: The positive PMIDs for training\n
    - pos_pmids_test: The positive PMIDs for testing\n
    - neg_pmids_train: The negative PMIDs for training\n
    - neg_pmids_test: The negative PMIDs for testing
    """
    
    pos_labels = np.ones(len(pos_pmids))
    neg_labels = np.zeros(len(neg_pmids))
    
    pmids = np.concatenate((pos_pmids, neg_pmids))
    labels = np.concatenate((pos_labels, neg_labels))
    
    # Split the data into training and testing sets
    pmids_train, pmids_test, labels_train, labels_test = train_test_split(
        pmids, labels, 
        test_size=split_size, 
        random_state=random_state
        )
    
    # Slice the embedding-dictionaries with the training and testing PMIDs
    pos_pmids_train = pmids_train[labels_train == 1]
    
    pos_pmids_test = pmids_test[labels_test == 1]
    
    neg_pmids_train = pmids_train[labels_train == 0]
    
    neg_pmids_test = pmids_test[labels_test == 0]    

    return pos_pmids_train, pos_pmids_test, neg_pmids_train, neg_pmids_test


if __name__ == "__main__":
    
    # Create a parser object and add arguments
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", dest="pos_file", required=True, help="Provide the path to the positive pmid file")
    parser.add_argument("-n", dest="neg_file", required=True, help="Provide the path to the negative pmid file")
    parser.add_argument("-o", dest="output_folder", required=True, help="Provide the path to the output folder")

    # Read arguments from the command line
    args=parser.parse_args()
            
    # Read the positive and negative pmids from the txt files
    with open(args.pos_file) as file:
        pos_pmids = file.read().splitlines()
        
    with open(args.neg_file) as file:
        neg_pmids = file.read().splitlines()
        
    pos_pmids = np.array(pos_pmids)
    neg_pmids = np.array(neg_pmids)
    
    # Create the training and testing sets
    pos_train, pos_test, neg_train, neg_test = make_datasets(
        pos_pmids=pos_pmids,
        neg_pmids=neg_pmids,
        split_size=0.2,
        random_state=42
        )
    
    # Save as txt files
    np.savetxt(args.output_folder + "POS_PMIDS_train.txt", pos_train, fmt='%s')
    np.savetxt(args.output_folder + "POS_PMIDS_test.txt", pos_test, fmt='%s')
    np.savetxt(args.output_folder + "NEG_PMIDS_train.txt", neg_train, fmt='%s')
    np.savetxt(args.output_folder + "NEG_PMIDS_test.txt", neg_test, fmt='%s')
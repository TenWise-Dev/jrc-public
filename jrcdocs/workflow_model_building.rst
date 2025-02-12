Model building
==============

This workflow describes the building of a simple model for classification. The purpose of such a classification model is to predict, on basis of an abstract of an article, whether an article describes a NAM and if so, for which disease the NAM is used and possibly also, which type of NAM is being described. The general set-up of the modelling flow is described in the figure below. 

.. image:: /images/modelling_flow.png


Constructing the data sets
--------------------------

As a first step we need a positive and a negative data set. The positive set in this example is the entire set of positive abstracts. As a negative set we use a random set of 2000 articles. The data sets can be found in the data directory. The construction of the sets, from queries and edicated sets of PMIDs is described in the Database building section.

Feature generation
------------------

There are a number of scripts that can be used for the conversion of the articles into feature tables, which can subsequently be used for classification. They are described in detail in the Scripts/Modelling section. Typically the usage is


Run the script ::

    # Use same wokring dir as in th eother example
    workdir=/tmp/examplejrc/

    ./PMID2Embed.py \
    -p ../data/POS_PMID_List_2024_03_17.txt \
    -d ../data/POS_Database_2024_03_17.json \
    -e abstract \
    -o $workdir/pos.npz

The resulting file is an npz data object that serves as input file for the model building script. In a similar way we can create a file for the negatve data set by running ::

    ./PMID2Embed.py \
    -p ../data/NEG_PMID_List_2024_02_21.txt \
    -d ../data/NEG_Database_2024_02_21.json \
    -e abstract \
    -o $workdir/neg.npz

 
Create the model
----------------

Next we use the embeddings for the positive and negative articles as input for the modelling script, using the following call ::

   ./PMID2Model.py \
   -p $workdir/pos.npz \
   -n $workdir/neg.npz \
   -c ../example/demo_config.json \
   -m $workdir/


This yields 2 types of output. The first is a table with the overview statistics ::

    Results:
                                     Accuracy  Precision  Recall    F1  Roc_auc
    Model               Dataset
    AdaBoost            test         0.76       0.94    0.60  0.73     0.78
                        train        0.76       0.93    0.59  0.72     0.79
                        val          0.75       0.93    0.59  0.72     0.79
    GradientBoost       test         0.79       0.95    0.66  0.78     0.81
                        train        0.80       0.93    0.67  0.78     0.82
                        val          0.79       0.93    0.67  0.78     0.81
    Logistic Regression test         0.79       0.95    0.66  0.78     0.81
                        train        0.79       0.93    0.67  0.78     0.81
                        val          0.79       0.93    0.67  0.77     0.81
    Random Forest       test         0.79       0.95    0.66  0.78     0.81
                        train        0.80       0.94    0.67  0.78     0.82
                        val          0.79       0.93    0.66  0.77     0.82
    Models saved to /tmp/


Double check the model
----------------------

One of the dangers of using high dimensional data for model building is that the model maybe overfitting on the supplied data. The script already takes measures to avoid this by using internal and external cross validation. Nevertheless it is good to do some additional checks with the model. For example, if we supply the script with two data sets that are esentailly equal, the models should end up being very unspecific.

Checking on positive and negative sets that are essentially equal can be done by drawing both sets from the same master data set. ::

    shuf  ../data/POS_PMID_List_Feb_2024.txt | head -500 > /tmp/negative_pmids.txt
    shuf  ../data/POS_PMID_List_Feb_2024.txt | head -500 > /tmp/positive_pmids.txt

    ./PMID2Embed.py \
    -p /tmp/positive_pmids.txt \
    -d ../data/POS_Database_Feb_2024.json \
    -o /tmp/pos.npz

    ./PMID2Embed.py \
    -p /tmp/negative_pmids.txt \
    -d ../data/POS_Database_Feb_2024.json \
    -o /tmp/neg.npz

    ./PMID2Model.py \
    -p /tmp/pos.npz \
    -n /tmp/neg.npz \
    -c ../example/demo_config.json \
    -m /tmp/

   

This gives the following results. This shows that the models have, as expected hardly any discriminatory power indicating that overfitting is not likely.::

    Results:
                                Accuracy  Precision  Recall    F1  Roc_auc
    Model               Dataset
    AdaBoost            test         0.43       0.44    0.48  0.46     0.43
                        train        0.83       0.83    0.84  0.83     0.92
                        val          0.43       0.43    0.44  0.44     0.40
    GradientBoost       test         0.44       0.44    0.46  0.45     0.44
                        train        0.93       0.92    0.93  0.93     0.99
                        val          0.41       0.41    0.40  0.40     0.36
    Logistic Regression test         0.49       0.49    0.52  0.50     0.49
                        train        0.70       0.70    0.70  0.69     0.76
                        val          0.43       0.44    0.44  0.43     0.43
    Random Forest       test         0.42       0.43    0.44  0.44     0.42
                        train        0.93       0.93    0.92  0.93     0.99
                        val          0.41       0.42    0.42  0.41     0.37


Using the model
---------------

The model can now be used for doing predictions. See the corresponding workflow for this.
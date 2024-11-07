Predicting abstracts
====================

This workflow describes the usage of the existing models to run a prediction on the abstracts. Here we describe a prediction with a single embedding. A shell script wrapper for all embedding methods is available in the repository.

An embedding with sentence transformers is done as follows ::

    ./PMID2Embed.py \
    -p $workdir/tmp_pmids.txt \
    -d $workdir/tmp_json.txt \
    -o $workdir/embedding.npz 

    # Which produces some diagnostic output

    11:54:56 - Getting abstracts from the database...
    11:54:56 - PMIDs with no abstracts: 0
    11:54:56 - Loading model...
    11:54:59 - Done loading model
    -----------------------------
    11:54:59 - Embedding abstracts...
    11:54:59 - Done, saving results to output file
    ----------------------------------------------

The embedding can now be used in a prediction script. It is important to do this with the correct model file. It does not make sense to predict with a model that was trained on Inverse Document Frequencies on an embedding with transformers. ::

    ./PMID2Predict.py \
    -e $workdir/embedding.npz \
    -m ../classifier_models/transformer/randomforest.pkl \
    -o $workdir/predictions.json

This gives the following output ::

    {
    "39468757": {
        "Prediction": 1,
        "Probability": 0.737,
        "Model": "RandomForestClassifier"
    },
    "39468028": {
        "Prediction": 1,
        "Probability": 0.695,
        "Model": "RandomForestClassifier"
    },
    "39465429": {
        "Prediction": 1,
        "Probability": 0.614,
        "Model": "RandomForestClassifier"
    },

This JSON file can now be merged back into the original database if required. ::

    ./DatabaseMerge.py \
    -j $workdir/tmp_json.txt \
    -u $workdir/predictions.json \
    -o $workdir/database_with_predictions.json

This yields additional fields in the JSON database like ::

    .....
        "issn": "2157-6580 (Electronic) 2157-6564 (Linking)",
        "mesh": "",
        "substances": "",
        "Prediction": 1,
        "Probability": 0.737,
        "Model": "RandomForestClassifier"
    },

However, since we have multiple models and multiple embeddings, this approach should be done in a looped way in a shell script. These are available in the lib directory. 

.. warning::
    Since we are still working on the models, these shell scripts are work in progress! Als we may find that the original scripts on which the shell scripts are build need to be addopted as the project progresses. So do not build production type workflows yet, but only use these scripts for inspiration. The shell scripts that we currently have are ::

        workflow_process_results.sh
        workflow_modelling.sh
        workflow_predict.sh
        workflow_predict_new.sh
        workflow_pdf2text.sh


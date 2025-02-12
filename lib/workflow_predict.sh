: '
 
*****************************
Workflow for predicting pmids
*****************************
 
This script is used to predict the pmids using the models trained on the embeddings.
The embedding types are: transformer, doc2vec, tfidf, bag of words (positive keywords)
The models used for prediction are: randomforest, adaboost, logistic_regression, gradientboost

USAGE ::
 
    workflow_predict.sh <workdir> <repodir> <pmid_file> <json_file> <email>
 
'
 
### END_OF_DOCSTRING ###
 

#!/usr/bin/bash

# ARGUMENTS
workdir=$1
repodir=$2
pmid_file=$3
json_file=$4
email=$5

# Directories
scriptdir=$repodir"/lib/"
embed_modeldir=$repodir"/embedding_models/"
classifierdir=$repodir"/classifier_models/May_set007/"

# Keywords file
pos_keyword_file=$embed_modeldir/pos_keywords.txt

# Check if all the required files exist
for file in $pmid_file $pos_keyword_file; do
    if [ ! -f "$file" ]; then
        echo "Could not find file: $file"
        exit 1
    fi
done

# Check if the required directories exist
for dir in $workdir $repodir $scriptdir $embed_modeldir $classifierdir; do
    if [ ! -d "$dir" ]; then
        echo "Could not find directory: $dir"
        exit 1
    fi
done

echo " DATABASE CREATION"
echo "================================="

# Check if predictions directory exists, if not create it
if [ ! -d "$workdir/predictions" ]; then
    mkdir $workdir/predictions
fi

# Check if database file exists, if not create it
if [ -f $json_file ]; then
     echo "Skipping database creation due to presence of $json_file"
else    
    echo "Creating database: $json_file"
    python3 "$scriptdir"PMID2Database.py \
     -p $pmid_file \
     -j $json_file \
     -e $email \
     -r $workdir/predictions/pmid_records.txt
fi

# Check if embedding directory exists, if not create it
if [ ! -d "$workdir/embeddings" ]; then
    mkdir $workdir/embeddings
fi

echo ""
echo " MODEL PREDICTIONS"
echo "================================="

# Create list of models and their corresponding postfixes and scripts
mymodels=("randomforest" "adaboost" "logistic_regression" "gradientboost")
model_postfixes=("transformer" "doc2vec" "tfidf") # Can add "bow_pos"
postfix_scripts=("PMID2Embed.py" "PMID2Doc2Vec.py" "PMID2Tfidf.py") # Can add "PMID2BOW.py"

# Loop through the postfixes to create embeddings and predict
for i in "${!model_postfixes[@]}"; do
    model_postfix=${model_postfixes[$i]}
    postfix_script=${postfix_scripts[$i]}

    # Check if embedding exists, if not create it
    if [ -f "$workdir/embeddings/embedding_$model_postfix.npz" ]; then
        echo "Skipping embedding for $model_postfix"
    else
        # Create embeddings based on the model postfix
        # DOC2VEC
        if [ $model_postfix == "doc2vec" ]; then
            echo "Creating $workdir/embeddings/embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pmid_file \
                -d $json_file \
                -o "$workdir/embeddings/embedding_$model_postfix.npz" \
                -e abstract \
                --load-model $embed_modeldir"doc2vec.model"
        # TFIDF
        elif [ $model_postfix == "tfidf" ]; then
            echo "Creating $workdir/embeddings/embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pmid_file \
                -d $json_file \
                -o "$workdir/embeddings/embedding_$model_postfix.npz" \
                -e abstract \
                --load-model $embed_modeldir"tfidf-3.joblib"
        # BOW (POSITIVE KEYWORDS)
        elif [ $model_postfix == "bow_pos" ]; then
            echo "Creating $workdir/embeddings/embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -j $json_file \
                -k $pos_keyword_file \
                -e abstract \
                -o "$workdir/embeddings/embedding_$model_postfix.npz"
        # TRANSFORMER
        else
            echo "Creating $workdir/embeddings/embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pmid_file \
                -d $json_file \
                -e abstract \
                -o "$workdir/embeddings/embedding_$model_postfix.npz"
        fi
    fi
    echo "---------------------------------"
    echo "Predicting for $model_postfix"
    # Loop through the models to predict
    for mymodel in "${mymodels[@]}"
        do
        # If prediction file exists, skip
        if [ -f $workdir/predictions/scores_"$mymodel"_"$model_postfix".json ]; then
            echo "Skipping predictions for $mymodel"
        else
            echo "Predicting with model: $mymodel"
            python3 "$scriptdir"PMID2Predict.py \
            -e "$workdir/embeddings/embedding_$model_postfix.npz" \
            -m $classifierdir/$model_postfix/$mymodel.pkl \
            -o $workdir/predictions/scores_"$mymodel"_"$model_postfix".json
        fi
        done
    echo "================================="
    echo ""
done
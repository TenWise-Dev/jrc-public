#!/usr/bin/bash

# DEFAULTS
scriptdir="PATH TO LIB"
modeldir="PATH TO MODELS"
pos_keyword_file="PATH TO POSITIVE KEYWORDS"
neg_keyword_file="PATH TO NEGATIVE KEYWORDS"

workdir=$1
prefix=$2
email=$3

pmid_file=$workdir/predictions/$prefix/predict_pmids.txt
json_file="${pmid_file%.txt}.json"
echo $json_file
if [ -f $json_file ]; then
     echo "Skipping $json_file"
else    
    echo "Creating $json_file"
    python3 "$scriptdir"PMID2Database.py \
     -p $pmid_file \
     -j $json_file \
     -e $email \
     -r $workdir/pmid_records.txt
fi

mymodels=("randomforest" "adaboost" "logistic_regression" "gradientboost")
model_postfix="transformer"
python3 "$scriptdir"PMID2Embed.py \
    -p $pmid_file \
    -d $json_file \
    -o $workdir/predictions/$prefix/embedding_$model_postfix.npz

for mymodel in "${mymodels[@]}"
    do
    python3 "$scriptdir"PMID2Predict.py \
    -e $workdir/predictions/$prefix/embedding_$model_postfix.npz \
    -m $workdir/models/$model_postfix/$mymodel.pkl \
    -o $workdir/predictions/$prefix/scores_"$mymodel"_"$model_postfix".json
    done

#Next run the embedding with Doc2Vec

model_postfix=doc2vec
python3 "$scriptdir"PMID2Doc2Vec.py \
 -p $pmid_file \
 -d $json_file \
 -o $workdir/predictions/$prefix/embedding_$model_postfix.npz \
 --load-model $embedding_modeldir/doc2vec.model

for mymodel in "${mymodels[@]}"
    do
    python3 "$scriptdir"PMID2Predict.py \
    -e $workdir/predictions/$prefix/embedding_$model_postfix.npz \
    -m $workdir/models/$model_postfix/$mymodel.pkl \
    -o $workdir/predictions/$prefix/scores_"$mymodel"_"$model_postfix".json
    done

    
model_postfix=tfid
python3 "$scriptdir"PMID2Tfidf.py \
 -p $pmid_file \
 -d $json_file \
 -o $workdir/predictions/$prefix/embedding_$model_postfix.npz \
 --load-model $embedding_modeldir/tfidf-3.joblib

for mymodel in "${mymodels[@]}"
    do
    python3 "$scriptdir"PMID2Predict.py \
    -e $workdir/predictions/$prefix/embedding_$model_postfix.npz \
    -m $workdir/models/$model_postfix/$mymodel.pkl \
    -o $workdir/predictions/$prefix/scores_"$mymodel"_"$model_postfix".json
    done

model_postfix=bow_pos
python3 "$scriptdir"PMID2BOW.py \
 -j $json_file \
 -k $pos_keyword_file \
 -o $workdir/predictions/$prefix/embedding_$model_postfix.npz

for mymodel in "${mymodels[@]}"
    do
    python3 "$scriptdir"PMID2Predict.py \
    -e $workdir/predictions/$prefix/embedding_$model_postfix.npz \
    -m $workdir/models/$model_postfix/$mymodel.pkl \
    -o $workdir/predictions/$prefix/scores_"$mymodel"_"$model_postfix".json
    done

model_postfix=bow_neg
python3 "$scriptdir"PMID2BOW.py \
 -j $json_file \
 -k $neg_keyword_file \
 -o $workdir/predictions/$prefix/embedding_$model_postfix.npz
    
for mymodel in "${mymodels[@]}"
    do
    python3 "$scriptdir"PMID2Predict.py \
    -e $workdir/predictions/$prefix/embedding_$model_postfix.npz \
    -m $workdir/models/$model_postfix/$mymodel.pkl \
    -o $workdir/predictions/$prefix/scores_"$mymodel"_"$model_postfix".json
    done
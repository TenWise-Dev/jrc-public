#!/usr/bin/bash

#set workdir
# workdir=PATH TO WORKDIR
myembeddings=("doc2vec" "biobert" )
mymodels=("randomforest" "adaboost" "logistic_regression" "gradientboost")

for myembed in "${myembeddings[@]}"
do
# Next run the embedding with Doc2Vec
cat $workdir/predictions_*_$myembed.json |  \
 jq -r 'to_entries[] | "\(.key)\t\(.value.Prediction)\t\(.value.Probability)\t\(.value.Model)"' > $workdir/"$myembed"_all_results.tsv
done 

awk -F'\t' '$2 == 1  && $3>0.8' $workdir/*all_results.tsv \
| awk '{print $1}' \
| sort | uniq -c | sort -n -r |head -10| awk '{print $2,$1}' > \
$workdir/top10_pmids.txt
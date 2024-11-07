#!/usr/bin/bash

#set workdir

workdir=$1
pos_pmid_file=$2
pos_dbjs_file=$3
neg_pmid_file=$4
neg_dbjs_file=$5

mkdir -p $workdir/models/
# scriptdir=PATH TO LIB
# modeldir=PATH TO MODELS

#First do some embedding with transformers
# model_postfix="transformer"
# mkdir $workdir/models/$model_postfix/
# python3 "$scriptdir"PMID2Embed.py \
# -p $pos_pmid_file \
# -d $pos_dbjs_file \
# -o $workdir/models/$model_postfix/embedding_pos.npz

# python3 "$scriptdir"PMID2Embed.py \
# -p $neg_pmid_file \
# -d $neg_dbjs_file \
# -o $workdir/models/$model_postfix/embedding_neg.npz


# python3 "$scriptdir"PMID2Model.py \
# -p $workdir/models/$model_postfix/embedding_pos.npz \
# -n $workdir/models/$model_postfix/embedding_neg.npz \
# -c "$scriptdir"/config_modeling.json \
# -m $workdir/models/$model_postfix/


# Next run the embedding with Doc2Vec

# model_postfix=doc2vec
# mkdir $workdir/models/$model_postfix/
# python3 "$scriptdir"PMID2Doc2Vec.py \
# -p $pos_pmid_file \
# -d $pos_dbjs_file \
# -o $workdir/models/$model_postfix/embedding_pos.npz

# python3 "$scriptdir"PMID2Doc2Vec.py \
# -p $neg_pmid_file \
# -d $neg_dbjs_file \
# -o $workdir/models/$model_postfix/embedding_neg.npz


# python3 "$scriptdir"PMID2Model.py \
# -p $workdir/models/$model_postfix/embedding_pos.npz \
# -n $workdir/models/$model_postfix/embedding_neg.npz \
# -c "$scriptdir"/config_modeling.json \
# -m $workdir/models/$model_postfix/



model_postfix=tfid
python3 "$scriptdir"PMID2Tfidf.py \
-p $pos_pmid_file \
-d $pos_dbjs_file \
-o $workdir/models/$model_postfix/embedding_pos.npz \
--load-model $modeldir/tfidf-3.joblib

python3 "$scriptdir"PMID2Tfidf.py \
-p  $neg_pmid_file \
-d $neg_dbjs_file \
-o $workdir/models/$model_postfix/embedding_neg.npz \
--load-model $modeldir/tfidf-3.joblib

# Next we do the modelling
mkdir $workdir/models/$model_postfix/
python3 "$scriptdir"PMID2Model.py \
-p $workdir/models/$model_postfix/embedding_pos.npz \
-n $workdir/models/$model_postfix/embedding_neg.npz \
-c "$scriptdir"/config_modeling.json \
-m $workdir/models/$model_postfix/




: '
 
*****************************
Workflow for creating models
*****************************
 
This script is used to create the models using the embeddings.
The embedding types are: transformer, doc2vec, tfidf, bag of words (positive keywords)
The models used for prediction are: randomforest, adaboost, logistic_regression, gradientboost

The embedding_type argument is used to specify the data type for the embeddings. 
The options are title, abstract, title_abstract

Optional are the model_indices and postfix_indices arguments.
The model_indices argument is used to specify the comma-separated indices of the models to be used. Options are 0: randomforest, 1: adaboost, 2: logistic_regression, 3: gradientboost.
The postfix_indices argument is used to specify the comma-separated indices of the embedding methods to be used. Options are 0: transformer, 1: doc2vec, 2: tfidf.

USAGE ::
 
    workflow_modelling.sh <workdir> <repodir> <pos_pmid_file> <pos_dbjs_file> <neg_pmid_file> <neg_dbjs_file> <embedding_type> <model_indices> <postfix_indices>
 
'
 
### END_OF_DOCSTRING ###
 

#!/usr/bin/bash

# ARGUMENTS
workdir=$1
repodir=$2
pos_pmid_file=$3
pos_dbjs_file=$4
neg_pmid_file=$5
neg_dbjs_file=$6
embedding_type=$7

# Directories
scriptdir=$repodir"/lib/"
embed_modeldir=$repodir"/embedding_models/"

# Embedding model options from fastest to slowest
# minilml6 (default) / minilml12 / roberta / mpnetv2
embed_model="minilml6"

echo ""
echo " MODELLING SETUP"
echo "================================="

echo "Workdir: $workdir"
echo ""
echo "Checking if the required files exist..."
echo "---------------------------------"

# Check if the required files exist
for file in $pos_pmid_file $pos_dbjs_file $neg_pmid_file $neg_dbjs_file; do
    if [ ! -f "$file" ]; then
        echo "Could not find file: $file"
        exit 1
    fi
done

echo ""
echo "Checking if the required directories exist..."
echo "---------------------------------"

# Check if the required directories exist
for dir in $workdir $repodir $scriptdir $embed_modeldir; do
    if [ ! -d "$dir" ]; then
        echo "Could not find directory: $dir"
        exit 1
    fi
done

# If there is no embeddings directory, create one
if [ ! -d "$workdir/embeddings" ]; then
    mkdir -p $workdir/embeddings
    echo "Created embeddings directory"
fi

# Do the same for models
if [ ! -d "$workdir/models" ]; then
    mkdir -p $workdir/models
    echo "Created models directory"
fi

# Create subdirectories for each model postfix
for model_postfix in "transformer" "doc2vec" "tfidf"; do
    if [ ! -d "$workdir/models/$model_postfix" ]; then
        mkdir -p $workdir/models/$model_postfix
    fi
done

# Create results directory for storing the results
if [ ! -d "$workdir/results" ]; then
    mkdir -p $workdir/results
    echo "Created results directory"
fi

echo ""
echo "All required files and directories exist"

echo ""
echo " MODEL CREATION"
echo "================================="

# Create list of models and embeddings and their corresponding postfixes and scripts
mymodels=("randomforest" "adaboost" "logistic_regression" "gradientboost")
model_postfixes=("transformer" "doc2vec" "tfidf")
postfix_scripts=("PMID2Embed.py" "PMID2Doc2Vec.py" "PMID2Tfidf.py")

# Get indices from arguments $8 and $9
model_indices_arg=$8
postfix_indices_arg=$9

# Default slices (all elements)
selected_models=("${mymodels[@]}")
selected_postfixes=("${model_postfixes[@]}")

# Parse $8 and $9 to slice arrays
if [ -n "$model_indices_arg" ]; then
    IFS=',' read -ra model_indices <<< "$model_indices_arg"

    # If the largest index is greater than the length of the array, exit
    if [ "${model_indices[-1]}" -ge "${#mymodels[@]}" ]; then
        echo "Invalid model index: ${model_indices[-1]}" >&2
        echo "Available models: ${mymodels[@]}" >&2
        exit 1
    fi

    selected_models=()
    for index in "${model_indices[@]}"; do
        if [ "$index" -ge 0 ] && [ "$index" -lt "${#mymodels[@]}" ]; then
            selected_models+=("${mymodels[index]}")
        else
            echo "Invalid model index: $index" >&2
            exit 1
        fi
    done
fi

if [ -n "$postfix_indices_arg" ]; then
    IFS=',' read -ra postfix_indices <<< "$postfix_indices_arg"

    # If the largest index is greater than the length of the array, exit
    if [ "${postfix_indices[-1]}" -ge "${#model_postfixes[@]}" ]; then
        echo "Invalid postfix index: ${postfix_indices[-1]}" >&2
        echo "Available postfixes: ${model_postfixes[@]}" >&2
        exit 1
    fi

    selected_postfixes=()
    selected_postfix_scripts=()
    for index in "${postfix_indices[@]}"; do
        if [ "$index" -ge 0 ] && [ "$index" -lt "${#model_postfixes[@]}" ]; then
            selected_postfixes+=("${model_postfixes[index]}")
            selected_postfix_scripts+=("${postfix_scripts[index]}")
        else
            echo "Invalid postfix index: $index" >&2
            exit 1
        fi
    done
fi

# Print the selected arrays
echo "Selected models: ${selected_models[@]}"
echo "Selected postfixes: ${selected_postfixes[@]}"
echo "---------------------------------"

for i in "${!selected_postfixes[@]}"; do
    model_postfix=${selected_postfixes[$i]}
    postfix_script=${selected_postfix_scripts[$i]}
    
    # Create embeddings based on the model postfix
    # DOC2VEC
    if [ $model_postfix == "doc2vec" ]; then
        if [ -f "$workdir/embeddings/pos_embedding_$model_postfix.npz" ]; then
            echo "Skipping positive embedding for $model_postfix"
        else
            # POSITIVE DATASET
            echo "Creating $workdir/embeddings/pos_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pos_pmid_file \
                -d $pos_dbjs_file \
                -o "$workdir/embeddings/pos_embedding_$model_postfix.npz" \
                -e $embedding_type \
                --load-model $embed_modeldir"doc2vec.model"
        fi

        if [ -f "$workdir/embeddings/neg_embedding_$model_postfix.npz" ]; then
            echo "Skipping negative embedding for $model_postfix"
        else
            # NEGATIVE DATASET
            echo "Creating $workdir/embeddings/neg_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $neg_pmid_file \
                -d $neg_dbjs_file \
                -o "$workdir/embeddings/neg_embedding_$model_postfix.npz" \
                -e $embedding_type \
                --load-model $embed_modeldir"doc2vec.model"
        fi

    # TFIDF
    elif [ $model_postfix == "tfidf" ]; then
        if [ -f "$workdir/embeddings/pos_embedding_$model_postfix.npz" ]; then
            echo "Skipping positive embedding for $model_postfix"
        else
            # POSITIVE DATASET
            echo "Creating $workdir/embeddings/pos_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pos_pmid_file \
                -d $pos_dbjs_file \
                -o "$workdir/embeddings/pos_embedding_$model_postfix.npz" \
                -e $embedding_type \
                --load-model $embed_modeldir"tfidf-3.joblib"
        fi

        if [ -f "$workdir/embeddings/neg_embedding_$model_postfix.npz" ]; then
            echo "Skipping negative embedding for $model_postfix"
        else
            # NEGATIVE DATASET
            echo "Creating $workdir/embeddings/neg_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $neg_pmid_file \
                -d $neg_dbjs_file \
                -o "$workdir/embeddings/neg_embedding_$model_postfix.npz" \
                -e $embedding_type \
                --load-model $embed_modeldir"tfidf-3.joblib"
        fi
    else
        # TRANSFORMER
        if [ -f "$workdir/embeddings/pos_embedding_$model_postfix.npz" ]; then
            echo "Skipping positive embedding for $model_postfix"
        else
            # POSITIVE DATASET
            echo "Creating $workdir/embeddings/pos_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $pos_pmid_file \
                -d $pos_dbjs_file \
                -o "$workdir/embeddings/pos_embedding_$model_postfix.npz" \
                -e $embedding_type \
                -m $embed_model
        fi

        if [ -f "$workdir/embeddings/neg_embedding_$model_postfix.npz" ]; then
            echo "Skipping negative embedding for $model_postfix"
        else
            # NEGATIVE DATASET
            echo "Creating $workdir/embeddings/neg_embedding_$model_postfix.npz"
            python3 "$scriptdir$postfix_script" \
                -p $neg_pmid_file \
                -d $neg_dbjs_file \
                -o "$workdir/embeddings/neg_embedding_$model_postfix.npz" \
                -e $embedding_type \
                -m $embed_model
        fi
    fi
    
    echo "---------------------------------"
    echo "Creating models for $model_postfix"

    # Create comma-separated string of selected models
    selected_models_str=$(IFS=,; echo "${selected_models[*]}")

    echo "Creating models: ${selected_models[@]}"
    python3 "$scriptdir"PMID2Model.py \
    -p "$workdir/embeddings/pos_embedding_$model_postfix.npz" \
    -n "$workdir/embeddings/neg_embedding_$model_postfix.npz" \
    -c $scriptdir/config_modeling.json \
    -m $workdir/models/$model_postfix/ \
    -o $workdir/results/$model_postfix.csv \
    -ml $selected_models_str

    echo "================================="
    echo ""
done

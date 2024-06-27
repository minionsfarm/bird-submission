#!/bin/bash

# Check if the number of arguments is 2
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <SPLIT> <MODEL>"
    exit 1
fi

SPLIT=$1
# Check if SPLIT is either dev or test
if [ "$SPLIT" != "dev" ] && [ "$SPLIT" != "test" ]; then
    echo "Error: SPLIT must be either 'dev' or 'test'"
    exit 1
fi

MODEL=$2
# Check if MODEL is either dev or test
if [ "$MODEL" != "small" ] && [ "$MODEL" != "large" ]; then
    echo "Error: MODEL must be either 'small' or 'large'"
    exit 1
fi

# Map small to x and large to y
if [ "$MODEL" == "small" ]; then
    MODEL="20240603_052455"
elif [ "$MODEL" == "large" ]; then
    MODEL="20240528_220303"
fi

DATASET=$3
if [ -z "$DATASET" ]; then
    DATASET="bird_${SPLIT}"
fi
GPUS=$4
if [ -z "$GPUS" ]; then
    GPUS="4"
fi

set -x
TOKENIZERS_PARALLELISM=false python3 /home/minions/public/run.py \
    --split $SPLIT \
    --model_id $MODEL \
    --dataset $DATASET \
    --input_dir /home/root/bird \
    --output_dir /home/root/output \
    --num_gpus=$GPUS

#!/bin/bash

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

python /home/minions/public/run_evaluation.py \
    --data_mode $SPLIT \
    --data_path "/home/root/bird" \
    --predicted_sql_path_kg "/home/root/output/${DATASET}/${MODEL}"

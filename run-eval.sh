#!/bin/bash

HOME="/home/$(whoami)"

# Check if the number of arguments is 4
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <SPLIT> <MODEL> <INPUT_DIR> <OUTPUT_DIR>"
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

INPUT_DIR=$3
OUTPUT_DIR=$4
DATASET=$5
if [ -z "$DATASET" ]; then
    DATASET="bird_${SPLIT}"
fi

# Check if INPUT_DIR starts with $HOME and is not equal to $HOME
if [[ "$INPUT_DIR" != "$HOME"* || "$INPUT_DIR" == "$HOME" ]]; then
    echo "Error: INPUT_DIR must start with $HOME and not be equal to $HOME"
    exit 1
fi

# Check if OUTPUT_DIR starts with $HOME and is not equal to $HOME
if [[ "$OUTPUT_DIR" != "$HOME"* || "$OUTPUT_DIR" == "$HOME" ]]; then
    echo "Error: OUTPUT_DIR must start with $HOME and not be equal to $HOME"
    exit 1
fi

INPUT_DIR_ORIG=$INPUT_DIR
OUTPUT_DIR_ORIG=$OUTPUT_DIR
# Replace $HOME in INPUT_DIR with /home/root
INPUT_DIR="${INPUT_DIR/#$HOME/\/home\/root}"
OUTPUT_DIR="${OUTPUT_DIR/#$HOME/\/home\/root}"

mkdir -p ${OUTPUT_DIR_ORIG}/${DATASET}

set -x
docker run \
    --rm \
    --gpus all \
    --runtime=nvidia \
    -v "${HOME}:/home/root" \
    -e TOKENIZERS_PARALLELISM=false \
    minions.azurecr.io/bird \
    --model_id="${MODEL}" \
    --split="${SPLIT}" \
    --dataset="${DATASET}" \
    --input_dir="${INPUT_DIR}" \
    --output_dir="${OUTPUT_DIR}" \
    --num_gpus=4


python convert_format.py \
  --questions_filename=${INPUT_DIR_ORIG}/${SPLIT}/${SPLIT}.json \
  --output_queries_filename=${OUTPUT_DIR_ORIG}/${DATASET}/output-${MODEL}.sql \
  --output_filename=${OUTPUT_DIR_ORIG}/${DATASET}/output-${MODEL}.json

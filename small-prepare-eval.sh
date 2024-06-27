#!/bin/bash

PREFIX=https://minionsbirdsubmission2.blob.core.windows.net/models
USER=$(whoami)
NUM_THREADS=8

BASE_DIR="/home/${USER}/bird-submission"
# Define the input files and corresponding destination directories
declare -A FILES_AND_DIRS=(
    # ["70b.txt"]="/home/${USER}/models/Meta-Llama-3-70B-Instruct"
    # ["8b.txt"]="/home/${USER}/models/Meta-Llama-3-8B-Instruct"
    # ["large.txt"]="/home/${USER}/adapters/large"
    ["${BASE_DIR}/small.txt"]="/home/${USER}/adapters/small"
)

# Create the destination directories if they do not exist
for DEST_DIR in "${FILES_AND_DIRS[@]}"; do
    mkdir -p "$DEST_DIR"
done

# Function to download a single file into the specified directory
download_file() {
    local FILE=$1
    local DEST_DIR=$2
    local URL="$PREFIX/$FILE"
    wget -P "$DEST_DIR" "$URL"
}

export -f download_file
export PREFIX

# Function to handle downloads for a specific file and directory
download_from_file_to_dir() {
    local FILE_LIST=$1
    local DEST_DIR=$2
    cat "$FILE_LIST" | xargs -n 1 -P "$NUM_THREADS" -I {} bash -c 'download_file "$@"' _ {} "$DEST_DIR"
}

# Export function and variables for xargs
export -f download_from_file_to_dir

# Download files in parallel for each file and corresponding directory
for FILE_LIST in "${!FILES_AND_DIRS[@]}"; do
    DEST_DIR=${FILES_AND_DIRS[$FILE_LIST]}
    download_from_file_to_dir "$FILE_LIST" "$DEST_DIR"
done

mv /home/root/adapters/small /home/root/adapters/20240603_052455
# mv /home/root/adapters/large /home/root/adapters/20240528_220303

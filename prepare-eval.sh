#!/bin/bash

if ! command -v az &> /dev/null
then
    echo "Error: az command not found. Please install Azure CLI."
    exit 1
fi

mkdir ~/models ~/adapters

# Download models and adapters
ACCOUNT_NAME="minionsbirdsubmission2"
CONTAINER_NAME="models"
user=$(whoami)
DESTINATION_FOLDER="/home/${user}"

TARGET="models/Meta-Llama-3-70B-Instruct/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET \
  --max-connections 8
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

TARGET="models/Meta-Llama-3-8B-Instruct/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET \
  --max-connections 8
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

CONTAINER_NAME="adapters"
TARGET="adapters/large/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET \
  --max-connections 8
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

TARGET="adapters/small/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET \
  --max-connections 8
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

mv ~/adapters/small ~/adapters/20240603_052455
mv ~/adapters/large ~/adapters/20240528_220303

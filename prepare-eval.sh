#!/bin/bash

if ! command -v az &> /dev/null
then
    echo "Error: az command not found. Please install Azure CLI."
    exit 1
fi

cat <<EOF > /etc/docker/daemon.json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
EOF

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
  --pattern $TARGET
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

TARGET="models/Meta-Llama-3-8B-Instruct/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

TARGET="adapters/large/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

TARGET="adapters/small/*"
az storage blob download-batch \
  --account-name $ACCOUNT_NAME \
  --overwrite \
  -s $CONTAINER_NAME \
  -d $DESTINATION_FOLDER \
  --pattern $TARGET
echo "Download completed: $DESTINATION_FOLDER/$TARGET"

# Download a docker
docker pull minions.azurecr.io/bird

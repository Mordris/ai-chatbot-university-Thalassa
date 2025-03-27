#!/bin/bash

# Navigate to the backend directory (optional, if the script is not already inside it)
# cd "$(dirname "$0")"

# Define the paths for the data, utils, and script files
DATA_FOLDER="data"
UTILS_FOLDER="utils"
MERGE_TXT_FILE="$UTILS_FOLDER/merge_txt_files.py"
CREATE_FAISS_INDEX_FILE="$UTILS_FOLDER/create_faiss_index.py"
FAISS_INDEX_FILE="$DATA_FOLDER/faiss_index.bin"
METADATA_FILE="$DATA_FOLDER/metadata.npy"

# Delete the .bin and .npy files in the data folder
echo "Deleting .bin and .npy files in $DATA_FOLDER..."
rm -f $FAISS_INDEX_FILE $METADATA_FILE
echo "Deleted .bin and .npy files."

# Run merge_txt_files.py using python3
echo "Running merge_txt_files.py..."
python3 $MERGE_TXT_FILE
echo "merge_txt_files.py completed."

# Run create_faiss_index.py using python3
echo "Running create_faiss_index.py..."
python3 $CREATE_FAISS_INDEX_FILE
echo "create_faiss_index.py completed."

echo "Reload process completed successfully."

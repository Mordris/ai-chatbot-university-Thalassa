#!/bin/bash

# Navigate to the script's directory to ensure relative paths work
cd "$(dirname "$0")"

# Define the paths using environment variables from .env or defaults
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

DATA_FOLDER="${DATA_FOLDER:-data}" # Default to 'data' if not set
UTILS_FOLDER="utils"
TEXT_FOLDER="${TEXT_FOLDER:-extracted_texts}" # Default to 'extracted_texts'
MERGE_TXT_FILE="$UTILS_FOLDER/merge_txt_files.py"
CREATE_FAISS_INDEX_FILE="$UTILS_FOLDER/create_faiss_index.py"
FAISS_INDEX_FILE="${INDEX_FILE:-$DATA_FOLDER/faiss_index.bin}" # Default if not set
METADATA_FILE="${METADATA_FILE:-$DATA_FOLDER/metadata.npy}" # Default if not set

# Function to check if python3 command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Determine python command
if command_exists python3; then
  PYTHON_CMD="python3"
elif command_exists python; then
  PYTHON_CMD="python"
else
  echo "Error: Neither 'python3' nor 'python' command found. Please install Python."
  exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Activate virtual environment if it exists
if [ -d "venv/bin" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
  if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    # Decide whether to exit or continue without venv
    # exit 1
    echo "Warning: Continuing without virtual environment activated."
  fi
else
    echo "Warning: Virtual environment 'venv' not found. Running scripts using system Python."
fi


# Create directories if they don't exist
echo "Ensuring directories exist..."
mkdir -p "$DATA_FOLDER"
mkdir -p "$TEXT_FOLDER"
mkdir -p "$UTILS_FOLDER"


# Delete the .bin and .npy files in the data folder
echo "Deleting existing FAISS index and metadata files..."
rm -f "$FAISS_INDEX_FILE" "$METADATA_FILE"
if [ $? -eq 0 ]; then
    echo "Deleted existing index files (if any)."
else
    echo "Warning: Could not delete index files (they might not exist)."
fi


# Run merge_txt_files.py
echo "------------------------------------"
echo "Running merge_txt_files.py..."
echo "------------------------------------"
$PYTHON_CMD "$MERGE_TXT_FILE"
if [ $? -ne 0 ]; then
  echo "Error: merge_txt_files.py failed."
  exit 1
fi
echo "merge_txt_files.py completed."


# Run create_faiss_index.py
echo "------------------------------------"
echo "Running create_faiss_index.py..."
echo "------------------------------------"
$PYTHON_CMD "$CREATE_FAISS_INDEX_FILE"
if [ $? -ne 0 ]; then
  echo "Error: create_faiss_index.py failed."
  exit 1
fi
echo "create_faiss_index.py completed."

echo "------------------------------------"
echo "Reload process completed successfully."
echo "------------------------------------"

# Deactivate if sourced
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment."
    deactivate
fi
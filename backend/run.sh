#!/bin/bash

echo "Activating Virtual Environment..."
source venv/bin/activate

# Check if activation failed
if [ $? -ne 0 ]; then
  echo "Error: Failed to activate virtual environment. Make sure 'venv' exists and is set up correctly."
  exit 1
fi

# Check for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
  # Try loading from .env file if not set in environment
  if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
  fi

  # Check again after loading .env
  if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]; then
    echo "--------------------------------------------------------------------------"
    echo "Warning: OPENAI_API_KEY is not set or is set to the placeholder value."
    echo "Please set it in your environment or in the .env file."
    echo "The application will likely fail to connect to OpenAI."
    echo "--------------------------------------------------------------------------"
  fi
fi

# Start FastAPI Server using Uvicorn with reload enabled for development
echo "Starting FastAPI server on http://0.0.0.0:8000 with auto-reload..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Deactivate environment when script exits (optional, usually happens automatically)
# echo "Deactivating Virtual Environment..."
# deactivate
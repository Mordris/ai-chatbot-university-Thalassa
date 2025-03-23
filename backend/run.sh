#!/bin/bash

# Activate Virtual Environment
source venv/bin/activate

# Start Ollama in the Background
nohup ollama serve &

# Start FastAPI Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

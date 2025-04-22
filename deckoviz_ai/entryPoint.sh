#!/bin/bash

# Run Streamlit app 
source venv/bin/activate
# Export environment variables from .env
set -a
if [ -f ../.env ]; then
  source ../.env
fi
set +a
streamlit run streamlit/app.py

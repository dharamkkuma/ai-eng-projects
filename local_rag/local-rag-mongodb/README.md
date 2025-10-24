
# Local RAG (MongoDB) — Deployment Notes

This repository contains notes and commands for a local retrieval-augmented generation (RAG) setup using MongoDB.

## Prerequisites
- Homebrew (macOS)
- Conda (or Miniconda)
- MongoDB Atlas CLI
- Python 3.9+ (as defined in environment.yaml)

## Quick setup

Install Atlas CLI:
```bash
brew install mongodb-atlas-cli
```

Download sample data (example):
```bash
curl -O https://atlas-education.s3.amazonaws.com/sampledata.archive
```

Create and activate Conda environment:
```bash
conda env create -f environment.yaml
conda info --envs
conda activate local-mongodb-rag-chatbot
```

Install ipykernel (if needed):
```bash
conda install ipykernel -c conda-forge

# If kernel not registered, run:
python -m ipykernel install --user --name local-mongodb-rag-chatbot --display-name "Python (local-mongodb-rag-chatbot)"
```

When done:
```bash
conda deactivate
```

## Models

Embed model (Hugging Face):
- mixedbread-ai/mxbai-embed-large-v1

Example: download using huggingface_hub (Python):
```python
# pip install huggingface_hub
from huggingface_hub import snapshot_download
snapshot_download(repo_id="mixedbread-ai/mxbai-embed-large-v1", cache_dir="./models/mxbai-embed-large-v1")
```

Mistral 7B (GGUF) — ~4 GB (example source):
https://gpt4all.io/models/gguf/mistral-7b-openorca.gguf2.Q4_0.gguf

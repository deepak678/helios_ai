# Helios AI Non-Financial Risk Intelligence Prototype

A prototype operational risk intelligence system for Helios that analyzes non-financial risk issues and supports:
- thematic clustering of risk issues into risk themes,
- duplicate/similar issue detection using semantic embeddings,
- issue hygiene scoring with OpenAI to evaluate clarity and completeness,
- a modern Streamlit dashboard with visualizations and summary metrics.

## Description

This project provides a complete prototype combining a FastAPI backend and a Streamlit frontend. It loads a sample dataset of risk issues, encodes descriptions using `sentence-transformers`, groups similar issues into clusters, finds high-similarity duplicate issue pairs, and generates hygiene feedback via the OpenAI API.

## Features
- Thematic clustering using `sentence-transformers` and `KMeans`
- Duplicate detection using cosine similarity on embeddings
- OpenAI-backed hygiene scoring for clarity, completeness, and risk justification
- Streamlit dashboard with issue table, cluster distribution, duplicate pairs, and hygiene review
- Local fallback analysis when backend is unavailable
- README and `.gitignore` included for deployment

## Project Structure

```
helios_ai/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   └── analyze.py
│   ├── services/
│   │   ├── embedding.py
│   │   ├── clustering.py
│   │   ├── duplication.py
│   │   ├── hygiene.py
│   ├── utils/
│   │   └── preprocessing.py
├── data/
│   └── sample_issues.csv
├── ui/
│   └── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

1. Create and activate a Python environment:

```bash
cd /Users/niharikamarya/Documents/project_folders/Helios_use_case/helios_ai
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure OpenAI API key:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## Run Backend

```bash
cd /Users/niharikamarya/Documents/project_folders/Helios_use_case/helios_ai
uvicorn app.main:app --reload
```

## Run Frontend

```bash
cd /Users/niharikamarya/Documents/project_folders/Helios_use_case/helios_ai
python -m streamlit run ui/app.py
```

## Git Push Commands

To push this project to `https://github.com/deepak678/helios_ai.git`:

```bash
git init
git add .
git commit -m "Initial Helios AI prototype"
git remote add origin https://github.com/deepak678/helios_ai.git
git branch -M main
git push -u origin main
```

If the repo already exists locally or the remote was previously configured, use:

```bash
git remote set-url origin https://github.com/deepak678/helios_ai.git
git add .
git commit -m "Update Helios AI prototype"
git push origin main
```

## Notes
- Activate the same virtual environment before installing dependencies and running the app.
- The backend is required for the API-driven version, but the Streamlit UI can fall back to local analysis if needed.
- Set `OPENAI_API_KEY` to enable the hygiene checker.

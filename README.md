# Debugging-Agent
This agent implements a Suggestor-Checker-Corrector pipeline. This modular framework is designed to facilitate iterative refinement based on RAG approach focusing on multi-agent orchestration.
## Prerequisites

- **Python 3.11+** (tested with 3.11)
- **pip** for installing dependencies
- **Docker** + **Docker Compose**

## Setup (Python environment)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

## Build the Vector Database

The vector database is built using Python 3.11 Documentation downloaded from [source](https://docs.python.org/3.11/download.html). These text files are closest to natural language and provide suitable context for LLM models.

Run the database creation script to build the Chroma vector store:

```powershell
python retriever/database_creation.py
```

This will populate the local vector database files used by the retriever.

## Start the Docker Image (Docker Compose)

1. Change to the Docker Compose directory:

```powershell
cd retriever/docker_dataset
```

2. Create and start the Docker composition:

```powershell
docker compose build
docker compose up -d
```

This starts the service that exposes the vector database for the agent.

## Run Tests

After the vector database is ready and the Docker service is running, run the test package using the provided CLI flags:

```powershell
python -m test --file="<filename>" --max_attempts=<num>
```

Replace `<filename>` with the test file you want to debug and `<num>` with the maximum number of attempts.

##  Stop the Docker Service

When you are done:

```powershell
cd retriever/docker_dataset
docker compose down
```

## Notes

- The vector DB will be stored under `retriever/docker_dataset/python_docs_vector_db/chroma.sqlite3`.
- If you change document sources, re-run `python retriever/database_creation.py` before restarting Docker.

---

If you need help diagnosing failures, run the tests with a higher log level or inspect `logs/` for generated log output.

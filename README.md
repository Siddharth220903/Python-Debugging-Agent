# Debugging-Agent

An intelligent, multi-agent debugging framework that implements a **Suggestor-Evaluator-Corrector** pipeline. This modular system uses Retrieval-Augmented Generation (RAG) and LLM orchestration to automatically identify and fix runtime errors in Python code.

## Features

- **Automated Code Debugging**: Detects and fixes execution errors in Python files
- **Multi-Agent Pipeline**: 
  - LLM-1: Suggests fixes with minimal hallucination
  - LLM-2: Provides unbiased evaluation of proposed changes
  - LLM-3: Makes final corrections and applies changes
- **RAG-Enhanced**: Uses Python 3.11 documentation for contextual knowledge
- **Iterative Refinement**: Attempts correction up to a configurable maximum
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Prerequisites

- **Python 3.11+** (tested with Python 3.11)
- **pip** for dependency management
- **Docker** + **Docker Compose** (for vector database service)
- **Git**

## Quick Start

### 1. Environment Setup

Clone and navigate to the project:

```powershell
cd Debugging-Agent
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Build Vector Database

The system uses Python 3.11 documentation for RAG-based retrieval. Build the Chroma vector store:

```powershell
python -m database_creation
```

This creates the vector embeddings from Python documentation and stores them locally.

### 4. Start Docker Service

Navigate to the Docker directory and start the vector database service:

```powershell
cd docker_dataset
docker compose up -d
cd ..
```

### 5. Run Debugging Agent

Debug a Python file with automatic error correction:

```powershell
python -m debugging_agent --file="path/to/your/file.py" --max_attempts=7
```

**Parameters:**
- `--file`: Path to the Python file to debug (default: `./debugging_agent/sample.py`)
- `--max_attempts`: Maximum correction attempts (default: 3)

### 6. Stop Services

When finished:

```powershell
cd docker_dataset
docker compose down
cd ..
```


## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DEBUGGING AGENT PIPELINE                       │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   Knowledge     │
                    │  (Python Docs)  │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │ Create Database │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │       DB 📊      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ↓              ↓              ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Code to be   │ │   Execute    │ │   Read Code  │
    │  debugged ⭐ │ │              │ │              │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                 │
           └────────────────┼─────────────────┘
                            │
                            ↓
                    ┌──────────────────┐
                    │ Clean Terminal   │
                    │     Output       │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ↓                             ↓
    ┌──────────────────────────┐  ┌────────────────────┐
    │      LLM-1 Model         │  │ Relevant info from │
    │ • Less hallucination     │  │        DB          │
    │ • Returns suggested      │  │                    │
    │   changes                │  └────────────────────┘
    └────────┬─────────────────┘
             │
             ↓
    ┌──────────────────────────┐
    │     LLM-2 Model          │
    │ • Unbiased evaluation    │
    │ • Needs larger model     │
    │   (no prior context)     │
    └────────┬─────────────────┘
             │
      ┌──────┴──────┐
      │ passes eval?│
      │             │
    YES           NO
      │             │
      ↓             ↓
  ┌────────┐   ┌──────────────────────────┐
  │ LLM-3  │   │ Reattempt correction     │
  │ Model  │   │ using "new code" in ⭐  │
  │        │   └──────────────┬───────────┘
  └───┬────┘                  │
      │                       │
      ↓                       │
┌──────────────────┐          │
│ Execute "new     │◄─────────┘
│    code"         │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ passes? │
    │         │
   YES      NO
    │        │
    ↓        │
┌─────┐      │
│ End.│      │
└─────┘      │
             │
    (Loop back to correction)

NOTE: If we assume code being debugged as state of 
architecture, it is assumed that new state is at 
least as "good" as old state.
```

## Module Descriptions

### `debugging_agent` (`__main__.py`)
- Entry point for the debugging pipeline
- Orchestrates file reading, code execution, and LLM inference
- Implements retry logic with configurable max attempts
- Logs all operations for debugging

### `inference_models`
- **InferenceModel**: Base class for LLM interactions
- **CoderModel** (LLM-1): Generates code suggestions with reduced hallucination
- **EvaluatorModel** (LLM-2): Unbiased evaluation of proposed fixes
- **LLMModel** (LLM-3): Applies corrections to the original code

### `code_executor`
- Safely executes Python code in an isolated environment
- Captures stdout, stderr, and exception information
- Returns execution status and output

### `file_handler`
- Reads Python source files
- Writes corrected code back to files
- Handles file I/O errors gracefully

### `rag_retriever`
- Interfaces with Chroma vector database
- Retrieves relevant documentation context
- Enhances LLM prompts with RAG knowledge

### `database_creation`
- Builds Chroma vector database from Python 3.11 docs
- Downloads documentation text files
- Creates embeddings for efficient retrieval

## Dependencies

Key packages (see `requirements.txt` for full list):
- **huggingface_hub**: Model hub integration
- **langchain-chroma**: RAG vector store
- **sentence-transformers**: Embedding generation
- **chromadb**: Vector database
- **python-dotenv**: Environment variable management
- **google-genai**: LLM API integration

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```
# Add any required API keys or configuration
HUGGINGFACE_TOKEN=your_token_here
GOOGLE_API_KEY=your_key_here
```

### Model Configuration
See `inference_models/model_details.json` for model-specific settings (temperature, max_tokens, etc.)

## Testing

Run the sample debugging test:

```powershell
python -m debugging_agent --file="./debugging_agent/sample.py" --max_attempts=5
```

Check the generated logs in `logs/` directory for detailed execution traces.

## Workflow

1. **Read**: Load the Python file to debug
2. **Execute**: Run the file and capture execution errors
3. **Retrieve**: Query vector DB for relevant documentation
4. **Suggest** (LLM-1): Generate fix suggestions
5. **Evaluate** (LLM-2): Validate suggested changes
6. **Correct** (LLM-3): Apply corrections if evaluation passes
7. **Verify**: Re-execute corrected code
8. **Retry**: Loop if execution still fails (up to max_attempts)

## Troubleshooting

### Docker Service Issues
```powershell
# View service logs
docker compose logs -f

# Rebuild containers
docker compose down
docker compose up -d --build
```

### Vector Database Problems
```powershell
# Rebuild the database
python -m database_creation
```

### Python Environment Issues
```powershell
# Recreate virtual environment
Remove-Item -Recurse venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Check Logs
All operations are logged to timestamped files in `logs/`:
```powershell
Get-Content logs/run_2026-03-29_*.log -Tail 50
```

## License

See [LICENSE](LICENSE) file for licensing information.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All changes are logged appropriately
- Tests pass before submitting changes

---

**For detailed debugging information**, check the timestamped log files in the `logs/` directory. Each run creates a new log file with comprehensive execution traces.

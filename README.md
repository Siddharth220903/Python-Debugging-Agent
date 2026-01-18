
# Python Debugging Agent

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main module with the following command:

```bash
python src/main.py --file <arguments_file> --max_attempts <number>
```

### Arguments

- `--file`: Path to the python code file which needs to be corrected 
- `--max_attempts`: Maximum number of attempts (default = 3)

### Example

```bash
python src/main.py --file test/sample.py --max_attempts 3
```

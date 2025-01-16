# **Compiler Construction Project**

## Requirements

- Python 3.12 or higher
- PLY (Python Lex-Yacc) library

## Installation

### Using pip

1. Make sure you have Python 3.12+ installed
2. Install dependencies using pip:
   ```
   pip install ply>=3.11
   ```

### Using Poetry (Recommended)

1. Make sure you have Python 3.12+ installed
2. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```

## Running the Program

### Using pip

1. Place your input expressions in `src/input/input.txt`
2. Run the program:
   ```
   python main.py
   ```

### Using Poetry

1. Place your input expressions in `src/input/input.txt`
2. Run the program:
   ```
   poetry run python main.py
   ```

The program will generate three output files in the `src/output` directory:

- `laika.tok`: Tokenized output showing lexical analysis results
- `laika.bracket`: Parsed expressions in bracket notation
- `laika.csv`: Symbol table contents

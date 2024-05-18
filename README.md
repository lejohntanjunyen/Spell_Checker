# Spell Checker App

This project is a Spell Checker application that identifies and suggests corrections for misspelled words using a dictionary and a corpus-based bigram model. The application includes a graphical user interface (GUI) built with Tkinter.

## Project Structure

The project consists of the following directories and files:

### Data Folder
1. **oxford_dict**: Contains the base dictionary files.
2. **corpus.txt**: The corpus text used to train the bigram model.
3. **dictionary.csv**: The dictionary file generated from the base dictionary and the corpus.
4. **f1_strat.pdf**: The PDF file from which the corpus was extracted.

### Src Folder
1. **01_extract.py**: Script for extracting the dictionary and corpus.
2. **02_main.py**: The main script for the Spell Checker application.
3. **requirements.txt**: The file containing the list of required libraries to run the spell checker in a virtual environment.

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual Environment (recommended)

### Steps
1. **Clone the repository**:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv nlp_env
    source nlp_env/bin/activate  # On Windows use `nlp_env\Scripts\activate`
    ```

3. **Install the required libraries**:
    ```sh
    pip install -r src/requirements.txt
    ```

4. **Download NLTK data**:
    ```python
    python -c "import nltk; nltk.download('averaged_perceptron_tagger'); nltk.download('punkt')"
    ```

## Usage

### Extract Dictionary and Corpus
1. Navigate to the `src` directory:
    ```sh
    cd src
    ```

2. Run the extraction script:
    ```sh
    python 01_extract.py
    ```

This script will extract the dictionary and corpus from the provided data files and save them in the specified locations.

### Run the Spell Checker Application
1. Ensure you are in the `src` directory:
    ```sh
    cd src
    ```

2. Run the main application script:
    ```sh
    python 02_main.py
    ```

The application GUI will open. You can input text, check for spelling errors, and explore the dictionary.

## Project Details

### 01_extract.py
- **Purpose**: Extracts and processes the base dictionary and corpus.
- **Main Functions**:
    - `generate_base_dictionary(input)`: Extracts vocabulary from base dictionary files.
    - `extract_pdf(pdf_path, corpus_path, outdict_path)`: Extracts corpus from the PDF file and generates the dictionary CSV file.

### 02_main.py
- **Purpose**: Implements the Spell Checker application with a GUI.
- **Main Features**:
    - **Check Spelling**: Identifies and highlights misspelled words.
    - **Suggestions**: Provides spelling suggestions using edit distance and bigram models.
    - **Explore Dictionary**: Allows users to explore and search the dictionary.

### requirements.txt
- **Purpose**: Lists all necessary Python libraries to run the project.
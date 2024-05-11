# Import libraries 
import os
import numpy as np
import pandas as pd
from pdfminer.high_level import extract_text
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
import csv
import re

# Dictionary Paths 
oxdict_path = "/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/data/oxford_dict"
outdict_path = "/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/data/dictonary.csv"

# Corpus Paths
pdf_path = "/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/data/f1_strat.pdf"
corpus_path = "/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/data/corpus.txt"

# Base Dictionary Extraction
def generate_base_dictionary(input=oxdict_path):
    """
    Description: Extract vocabulary from base dictionary.
    Parameters:
        - input (str): Base dictionary directory.

    Return:
        - List of Extracted vocabulary from input files
    """

    # Initialise empty list
    all_words = []
    # Iterate over all files in the directory
    for filename in os.listdir(input):
        # Checking file type
        if filename.endswith(".csv"):
            # Join file path and file name to get full file path for import
            file_path = os.path.join(input, filename)
            # Aword and Dword files have unexpected EOF errors
            if filename == "Aword.csv" or filename == "Dword.csv":
                try:
                    # Required to use multiple encoding methods to cater all reading all files due to different bytes
                    for encoding_method in ['utf-8', 'latin-1', 'ISO-8859-1', 'Windows-1252', 'ISO-8859-15']:
                        # Included quoting parameter for unexpected EOF errors
                        df = pd.read_csv(file_path, header=None, encoding=encoding_method, quoting=csv.QUOTE_NONE)
                        # Remove duplicates and append unique words to the list
                        unique_words = df[0].unique().tolist()
                        # Add lists of unique words to existing list
                        all_words.extend(unique_words)
                        # Stop trying other encoding methods if successful
                        break
                    else:
                        # Continue to the next file if no successful encoding is found
                        continue
                except Exception as e:
                    # If an exception occurs, move to the next encoding method
                    pass 
            # For other files, read normally without error handling
            else:
                # Required to use multiple encoding methods to cater all reading all files due to different bytes
                for encoding_method in ['utf-8', 'latin-1', 'ISO-8859-1', 'Windows-1252', 'ISO-8859-15']:
                    try:
                        df = pd.read_csv(file_path, header=None, encoding=encoding_method)
                        # Remove duplicates and append unique words to the list
                        unique_words = df[0].unique().tolist()
                        # Add lists of unique words to existing list
                        all_words.extend(unique_words)
                        # Stop trying other encoding methods if successful
                        break  
                    except Exception as e:
                        # If an exception occurs, move to the next encoding method
                        pass  

    # Remove duplicates
    cleaned_dictionary = list(set(all_words))
    
    return cleaned_dictionary

# Corpus Extraction
def extract_pdf(pdf_path=pdf_path, corpus_path=corpus_path, outdict_path=outdict_path):
    
    """
    Description: Extract corpus from PDF file, with the use of pdfminer library. Generate dictionary csv file using base dictionary and extracted vocabulary from corpus. 
    Reference: https://vitalflux.com/python-extract-text-pdf-file-using-pdfminer/
    Parameters:
        - pdf_path      (str): PDF directory to extract corpus from.
        - corpus_path   (str): Output directory for corpus.
        - outdict_path  (str): Output directory for dicionary.
    Return:
        - List of filtered unique tokens from corpus.
    """

    # Extract corpus from PDF using PDFMiner library
    corpus = extract_text(pdf_path)
    # Remove all Non-letters from corpus
    cleaned_corpus = re.sub('[^A-Za-z]+',' ', corpus)
    # Save cleaned corpus into corpus.txt
    with open(corpus_path, "w") as text_file:
        text_file.write(cleaned_corpus)

    # Using regex tokenizer from NLTK library to tokenize words that match any word that starts with upper or lowercase letters followed by more characters
    tokenizer = RegexpTokenizer('[A-z]\w+')
    # Apply tokenizer to corpus
    words = tokenizer.tokenize(corpus)
    # Filter unique tokens
    unique_words = np.unique(words)
    # Generate the frequency for each token 
    frequency_words = FreqDist(words)
    
    # Initialise empty list
    filtered_unique_words = []
    # Each unique tokens
    for word in unique_words:
        # Remove token shorter than 1 length and frequency less than 3
        if len(word) > 1 and frequency_words[word] > 3:
            # Transform token to lowercase then append to list
            filtered_unique_words.append(word.lower())
    
    # Using previously defined function to generate base dictionary from oxford dictionary data
    base_dictionary = generate_base_dictionary()
    # Append the token extracted from corpus to base dictionary for a complete set of dictionary data
    new_dictionary = base_dictionary + filtered_unique_words
    
    # Initialise empty list
    unique_new_dictionary = []
    # Each word in new complete set of dictionary
    for _ in new_dictionary:
        # Remove any non-letter words from new complete set of dicitonary 
        cleaned_word = re.sub('[^a-zA-Z]+', '', _)
        unique_new_dictionary.append(cleaned_word)

    # Remove duplicates
    unique_new_dictionary = list(sorted(set(unique_new_dictionary)))

    # Export to dictionary CSV File
    with open(outdict_path, 'w') as f:
        write = csv.writer(f)
        write.writerow(unique_new_dictionary)

    # Print Summary of PDF, Corpus and Dictionary
    print(f"Number of Words in PDF               : {len(corpus)}")
    print(f"Number of Words in Base Dictionary   : {len(base_dictionary)}")
    print(f"Number of Words in New Dictionary    : {len(unique_new_dictionary)}")
    print(f"Number of Words in Corpus            : {len(cleaned_corpus)}")    
    print(f"Number of unique tokens              : {len(unique_words)}")
    print(f"Number of filtered unique tokens     : {len(filtered_unique_words)}")
    print("Extract complete")
    
    return filtered_unique_words

# Generate dictionary and corpus from Oxford dictionary data and scientific research paper
pdf_conent = extract_pdf(pdf_path)
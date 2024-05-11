import random
import re
from collections import defaultdict
from nltk.util import ngrams

def train_bigram_model(text):
    """
    Train a bigram language model using the given text.
    """
    # Tokenize text into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Generate bigrams
    bigrams = list(ngrams(words, 2))
    
    # Count the occurrences of each bigram
    bigram_counts = defaultdict(int)
    for bigram in bigrams:
        bigram_counts[bigram] += 1
    
    # Compute probabilities for each bigram
    bigram_model = defaultdict(dict)
    for (word1, word2), count in bigram_counts.items():
        bigram_model[word1][word2] = count / words.count(word1)
    
    return bigram_model

def generate_text(bigram_model, seed_word, num_words=20):
    """
    Generate text using the bigram language model starting from the seed word.
    """
    current_word = seed_word
    generated_text = [current_word]
    
    for _ in range(num_words):
        # Check if the current word exists in the bigram model
        if current_word in bigram_model:
            # Choose the next word based on the probabilities from the bigram model
            next_word = random.choices(list(bigram_model[current_word].keys()), 
                                        weights=list(bigram_model[current_word].values()))[0]
            generated_text.append(next_word)
            current_word = next_word
        else:
            break  # If the current word is not in the model, end the generation
        
    return ' '.join(generated_text)

def main():
    # Sample text for training the bigram model
    text = "The quick brown fox jumps over the lazy dog. The lazy dog sleeps all day."

    # Train the bigram model
    bigram_model = train_bigram_model(text)

    # Seed word to start generating text
    seed_word = "the"

    # Generate text using the bigram model
    generated_text = generate_text(bigram_model, seed_word, num_words=20)

    print("Generated Text:")
    print(generated_text)

if __name__ == "__main__":
    main()

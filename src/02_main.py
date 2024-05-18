# Import necessary libraries
import tkinter as tk
from tkinter import scrolledtext, Menu, messagebox, Toplevel, Listbox, Entry, Button
import csv
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.metrics.distance import edit_distance
from nltk.tag import pos_tag
from nltk.util import ngrams
import re

# Ensure necessary NLTK resources are downloaded
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')

# Define SpellingCheckerApp class which inherits from tk.Tk
class SpellingCheckerApp(tk.Tk):
    def __init__(self):
        # Call the parent class (tk.Tk) constructor
        super().__init__()

        # Set window title and dimensions
        self.title("Spelling Checker")
        self.geometry("800x600")

        # Create and pack a scrolled text widget for text input
        self.text_editor = scrolledtext.ScrolledText(self, width=100, height=20)
        self.text_editor.pack(expand=True, fill='both')
        self.text_editor.bind("<Button-2>", self.on_right_click)  # Bind right-click event

        # Create and pack a button to check spelling
        self.check_button = tk.Button(self, text="Check Spelling", command=self.check_spelling)
        self.check_button.pack()

        # Create and pack a scrolled text widget for output display
        self.output_display = scrolledtext.ScrolledText(self, width=100, height=10)
        self.output_display.pack(expand=True, fill='both')

        # Create and pack a button to explore the dictionary
        self.explore_button = tk.Button(self, text="Explore Dictionary", command=self.explore_dictionary)
        self.explore_button.pack()

        # Load resources (dictionary and corpus) and store them in instance variables
        self.dictionary, self.bigram_model, self.unigram_model = self.load_resources(
            '/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/dictonary.csv',
            '/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/corpus.txt'
        )

    def load_resources(self, dictionary_path, corpus_path):
        """
        Load the dictionary and corpus, then build unigram and bigram models.
        """
        # Load the dictionary from a CSV file
        dictionary = set()
        with open(dictionary_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                dictionary.update(row)

        # Load the corpus from a text file and process it
        with open(corpus_path, 'r', encoding='utf-8') as file:
            text = file.read().lower()
            tokens = word_tokenize(text)
            bigrams = list(ngrams(tokens, 2))
            bigram_counts = Counter(bigrams)
            unigram_counts = Counter(tokens)
            bigram_total = sum(bigram_counts.values())
            unigram_total = sum(unigram_counts.values())

            # Build bigram and unigram models
            bigram_model = {bigram: count / bigram_total for bigram, count in bigram_counts.items()}
            unigram_model = {word: count / unigram_total for word, count in unigram_counts.items()}

        # Return the loaded dictionary and models
        return dictionary, bigram_model, unigram_model

    def is_valid_bigram(self, word1, word2):
        """
        Check if a given bigram is valid based on the bigram model.
        """
        return (word1, word2) in self.bigram_model

    def check_spelling(self):
        """
        Check the spelling of the text entered in the text editor.
        """
        # Get text from the text editor and tokenize it
        text = self.text_editor.get("1.0", "end-1c").lower()
        tokens = word_tokenize(text)
        tagged_tokens = pos_tag(tokens)
        misspelled_words = []

        # Identify misspelled words
        for word, _ in tagged_tokens:
            if word not in self.dictionary:
                misspelled_words.append(word)

        # Display misspelled words in the output display
        self.output_display.insert(tk.END, f"Misspelled words identified: {misspelled_words}\n")
        self.highlight_misspelled_words(misspelled_words)

    def highlight_misspelled_words(self, words):
        """
        Highlight misspelled words in the text editor.
        Reference: https://stackoverflow.com/questions/24819123/how-to-get-the-index-of-word-being-searched-in-tkinter-text-box
        """
        # Configure the tag for misspelled words
        self.text_editor.tag_config("misspelled", foreground="red")
        for word in words:
            start_index = self.text_editor.search(word, "1.0", tk.END)
            while start_index:
                end_index = f"{start_index}+{len(word)}c"
                self.text_editor.tag_add("misspelled", start_index, end_index)
                start_index = self.text_editor.search(word, end_index, tk.END)

    def on_right_click(self, event):
        """
        Handle right-click events to show suggestions for the selected word.
        """
        try:
            # Determine the position of the right-clicked word
            position = self.text_editor.index(f"@{event.x},{event.y}")
            line_index = position.split('.')[0]
            line_content = self.text_editor.get(f"{line_index}.0", f"{line_index}.end")
            char_index = int(position.split('.')[1])
            words = list(re.finditer(r'\b\w+\b', line_content))
            
            for word in words:
                start, end = word.start(), word.end()
                if start <= char_index < end:
                    full_word = word.group(0)
                    full_position = f"{line_index}.{start}"
                    break
            else:
                self.output_display.insert(tk.END, "No word found at the cursor position.\n")
                return

            # Display the right-clicked word in the output display
            self.output_display.insert(tk.END, f"Right-clicked word: {full_word}\n")
            if full_word.lower() not in self.dictionary:
                self.create_suggestion_menu(event, full_word, full_position)
            else:
                self.output_display.insert(tk.END, f"'{full_word}' is spelled correctly or not detected properly.\n")
        except Exception as e:
            self.output_display.insert(tk.END, f"Error in on_right_click: {e}\n")

    def create_suggestion_menu(self, event, word, position):
        """
        Create a suggestion menu for a misspelled word.
        Reference: https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
        """
        # Create a menu and add suggestions to it
        menu = Menu(self, tearoff=0)
        suggestions = self.get_suggestions(word)
        self.output_display.insert(tk.END, f"Suggestions for {word}: {suggestions}\n")
        if suggestions:
            for suggestion in suggestions:
                menu.add_command(label=suggestion, command=lambda sug=suggestion, w=word: self.replace_word(position, w, sug))
            menu.post(event.x_root, event.y_root)
        else:
            self.output_display.insert(tk.END, "No suggestions found for this word.\n")

    def get_suggestions(self, word):
        """
        Get spelling suggestions for a misspelled word.
        """
        # Generate initial suggestions based on edit distance
        suggestions = [entry for entry in self.dictionary if edit_distance(word.lower(), entry) <= 2]
        
        # Refine suggestions using the bigram model
        if suggestions:
            prev_word = self.get_previous_word(word)
            if prev_word:
                suggestions = sorted(
                    suggestions,
                    key=lambda x: self.bigram_model.get((prev_word, x), 0),
                    reverse=True
                )
        
        return suggestions[:5]

    def get_previous_word(self, current_word):
        """
        Get the word that precedes the current word in the text.
        """
        text = self.text_editor.get("1.0", "end-1c").lower()
        tokens = word_tokenize(text)
        for i, word in enumerate(tokens):
            if word == current_word and i > 0:
                return tokens[i-1]
        return None

    def replace_word(self, position, word, suggestion):
        """
        Replace a misspelled word with a suggested correction.
        """
        # Replace the word in the text editor and update the output display
        self.text_editor.delete(position, f"{position} wordend")
        self.text_editor.insert(position, suggestion)
        self.output_display.insert("end", f"Replaced '{word}' with '{suggestion}'\n")

    def explore_dictionary(self):
        """
        Open a new window to explore the dictionary.
        """
        # Create a new window for dictionary exploration
        explorer = Toplevel(self)
        explorer.title("Dictionary Explorer")
        explorer.geometry("600x400")

        # Create and pack a label and entry for search
        search_label = tk.Label(explorer, text="Search Word:")
        search_label.pack()

        search_entry = tk.Entry(explorer)
        search_entry.pack()

        # Create and pack a listbox to display dictionary words
        word_listbox = Listbox(explorer, width=80, height=20)
        word_listbox.pack(expand=True, fill='both')

        # Add a scrollbar to the listbox
        scrollbar = tk.Scrollbar(word_listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        word_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=word_listbox.yview)

        # Display all words in the dictionary
        sorted_words = sorted(self.dictionary)
        for word in sorted_words:
            word_listbox.insert(tk.END, word)

        def search_word():
            """
            Search for a word in the dictionary and display matching results.
            """
            search_term = search_entry.get().lower()
            word_listbox.delete(0, tk.END)
            for word in sorted_words:
                if search_term in word:
                    word_listbox.insert(tk.END, word)

        # Create and pack a button to initiate search
        search_button = Button(explorer, text="Search", command=search_word)
        search_button.pack()

# Main block to run the application
if __name__ == "__main__":
    app = SpellingCheckerApp()
    app.mainloop()

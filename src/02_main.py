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
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

class SpellingCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spelling Checker")
        self.geometry("800x600")

        self.text_editor = scrolledtext.ScrolledText(self, width=100, height=20)
        self.text_editor.pack(expand=True, fill='both')
        self.text_editor.bind("<Button-2>", self.on_right_click)

        self.check_button = tk.Button(self, text="Check Spelling", command=self.check_spelling)
        self.check_button.pack()

        self.output_display = scrolledtext.ScrolledText(self, width=100, height=10)
        self.output_display.pack(expand=True, fill='both')

        self.explore_button = tk.Button(self, text="Explore Dictionary", command=self.explore_dictionary)
        self.explore_button.pack()

        self.dictionary, self.bigram_model, self.unigram_model = self.load_resources(
            '/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/dictonary.csv',
            '/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/corpus.txt')

    def load_resources(self, dictionary_path, corpus_path):
        dictionary = set()
        with open(dictionary_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                dictionary.update(row)

        with open(corpus_path, 'r', encoding='utf-8') as file:
            text = file.read().lower()
            tokens = word_tokenize(text)
            bigrams = list(ngrams(tokens, 2))
            bigram_counts = Counter(bigrams)
            unigram_counts = Counter(tokens)
            bigram_total = sum(bigram_counts.values())
            unigram_total = sum(unigram_counts.values())

            bigram_model = {bigram: count / bigram_total for bigram, count in bigram_counts.items()}
            unigram_model = {word: count / unigram_total for word, count in unigram_counts.items()}

        return dictionary, bigram_model, unigram_model

    def is_valid_bigram(self, word1, word2):
        return (word1, word2) in self.bigram_model

    def check_spelling(self):
        text = self.text_editor.get("1.0", "end-1c").lower()
        tokens = word_tokenize(text)
        tagged_tokens = pos_tag(tokens)
        prev_word = None
        misspelled_words = []

        for word, _ in tagged_tokens:
            # Check if the word is in the dictionary
            if word not in self.dictionary:
                misspelled_words.append(word)
            prev_word = word

        self.output_display.insert(tk.END, f"Misspelled words identified: {misspelled_words}\n")
        self.highlight_misspelled_words(misspelled_words)

    def highlight_misspelled_words(self, words):
        self.text_editor.tag_config("misspelled", foreground="red")
        for word in words:
            start_index = self.text_editor.search(word, "1.0", tk.END)
            while start_index:
                end_index = f"{start_index}+{len(word)}c"
                self.text_editor.tag_add("misspelled", start_index, end_index)
                start_index = self.text_editor.search(word, end_index, tk.END)

    def on_right_click(self, event):
        try:
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

            self.output_display.insert(tk.END, f"Right-clicked word: {full_word}\n")
            if full_word.lower() not in self.dictionary:
                self.create_suggestion_menu(event, full_word, full_position)
            else:
                self.output_display.insert(tk.END, f"'{full_word}' is spelled correctly or not detected properly.\n")
        except Exception as e:
            self.output_display.insert(tk.END, f"Error in on_right_click: {e}\n")

    def create_suggestion_menu(self, event, word, position):
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
        # Initial edit distance based suggestions
        suggestions = [entry for entry in self.dictionary if edit_distance(word.lower(), entry) <= 2]
        
        # Refine suggestions with bigram model
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
        text = self.text_editor.get("1.0", "end-1c").lower()
        tokens = word_tokenize(text)
        for i, word in enumerate(tokens):
            if word == current_word and i > 0:
                return tokens[i-1]
        return None

    def replace_word(self, position, word, suggestion):
        self.text_editor.delete(position, f"{position} wordend")
        self.text_editor.insert(position, suggestion)
        self.output_display.insert("end", f"Replaced '{word}' with '{suggestion}'\n")

    def explore_dictionary(self):
        explorer = Toplevel(self)
        explorer.title("Dictionary Explorer")
        explorer.geometry("600x400")

        search_label = tk.Label(explorer, text="Search Word:")
        search_label.pack()

        search_entry = tk.Entry(explorer)
        search_entry.pack()

        word_listbox = Listbox(explorer, width=80, height=20)
        word_listbox.pack(expand=True, fill='both')

        scrollbar = tk.Scrollbar(word_listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        word_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=word_listbox.yview)

        # Display all words in the dictionary
        sorted_words = sorted(self.dictionary)
        for word in sorted_words:
            word_listbox.insert(tk.END, word)

        def search_word():
            search_term = search_entry.get().lower()
            word_listbox.delete(0, tk.END)
            for word in sorted_words:
                if search_term in word:
                    word_listbox.insert(tk.END, word)

        search_button = Button(explorer, text="Search", command=search_word)
        search_button.pack()

if __name__ == "__main__":
    app = SpellingCheckerApp()
    app.mainloop()

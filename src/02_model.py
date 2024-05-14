import tkinter as tk
from tkinter import scrolledtext, Menu
import csv
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.metrics.distance import edit_distance
from nltk.tag import pos_tag 

nltk.download('averaged_perceptron_tagger')

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

        self.dictionary = self.load_dictionary('/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/dictonary.csv')

    def load_dictionary(self, filename):
        dictionary = set()
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                dictionary.update(row)
        return dictionary

    def check_spelling(self):
        text = self.text_editor.get("1.0", "end-1c")
        tokens = word_tokenize(text)
        tagged_tokens = pos_tag(tokens)  # Tagging each token
        self.highlight_misspelled_words([word for word, _ in tagged_tokens if word.lower() not in self.dictionary])
        self.detect_real_word_errors(tagged_tokens)  # New method to detect real-word errors

    def detect_real_word_errors(self, tagged_tokens):
        # This is a placeholder for a real implementation
        for word, tag in tagged_tokens:
            if word.lower() in ['their', 'there', 'they\'re']:
                self.output_display.insert("end", f"Check usage: {word} may be incorrect contextually.\n")
    
    def on_right_click(self, event):
        try:
            position = self.text_editor.index(f"@{event.x},{event.y}")
            # Adjust to get the entire word around the cursor
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
                print("No word found at the cursor position.")  # Debug output for no word found
                return

            print(f"Right-clicked word: {full_word}")  # Debugging output
            if full_word.lower() not in self.dictionary:
                self.create_suggestion_menu(event, full_word, full_position)
            else:
                print(f"'{full_word}' is spelled correctly or not detected properly.")  # Debugging output
        except Exception as e:
            print(f"Error in on_right_click: {e}")  # Print exceptions if any

    def create_suggestion_menu(self, event, word, position):
        menu = Menu(self, tearoff=0)
        suggestions = self.get_suggestions(word)
        print(f"Suggestions for {word}: {suggestions}")  # Debugging output
        if suggestions:
            for suggestion in suggestions:
                menu.add_command(label=suggestion, command=lambda sug=suggestion: self.replace_word(position, sug))
            menu.post(event.x_root, event.y_root)
        else:
            print("No suggestions found for this word.")  # Debugging output
    
    def get_suggestions(self, word):
        return [entry for entry in self.dictionary if edit_distance(word.lower(), entry) <= 2][:5]

    def replace_word(self, position, suggestion):
        self.text_editor.delete(position, f"{position} wordend")
        self.text_editor.insert(position, suggestion)
        self.output_display.insert("end", f"Replaced '{word}' with '{suggestion}'\n")
    
    def highlight_misspelled_words(self, words):
        self.text_editor.tag_config("misspelled", foreground="red")
        for word in words:
            start_index = self.text_editor.search(word, "1.0", "end")
            end_index = f"{start_index}+{len(word)}c"
            self.text_editor.tag_add("misspelled", start_index, end_index)

if __name__ == "__main__":
    app = SpellingCheckerApp()
    app.mainloop()

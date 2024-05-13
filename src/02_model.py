import tkinter as tk
from tkinter import scrolledtext, messagebox
import csv
from nltk.tokenize import word_tokenize
from nltk.metrics.distance import edit_distance

class SpellingCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spelling Checker")
        self.geometry("800x600")
        
        self.text_editor = scrolledtext.ScrolledText(self, width=100, height=20)
        self.text_editor.pack(expand=True, fill='both')
        
        self.check_button = tk.Button(self, text="Check Spelling", command=self.check_spelling)
        self.check_button.pack()
        
        self.suggestions_display = scrolledtext.ScrolledText(self, width=30, height=20)
        self.suggestions_display.pack(side="right", fill='y')
        self.suggestions_display.bind("<Button-1>", self.replace_word)

        self.undo_button = tk.Button(self, text="Undo", command=self.undo)
        self.undo_button.pack()

        self.selected_word = None
        
        # Load dictionary from the CSV file
        self.dictionary = self.load_dictionary('/Users/lejohn/Documents/APU/Natural_Language_Processing/NLP_Assignment/Spell_Checker/data/dictonary.csv')
        
    def load_dictionary(self, filename):
        dictionary = set()
        with open(filename, 'r', encoding='iso-8859-1') as file:
            reader = csv.reader(file)
            for row in reader:
                dictionary.update(row)
        return dictionary
        
    def check_spelling(self):
        text = self.text_editor.get("1.0", "end-1c")
        tokens = word_tokenize(text)
        misspelled_words = [word for word in tokens if word.lower() not in self.dictionary]
        
        if misspelled_words:
            self.suggestions_display.delete("1.0", "end")
            for word in misspelled_words:
                suggestions = self.get_suggestions(word)
                self.suggestions_display.insert("end", f"{word}: {', '.join(suggestions)}\n")
        else:
            messagebox.showinfo("No Misspelled Words", "No misspelled words found!")

    def get_suggestions(self, word):
        suggestions = []
        for entry in self.dictionary:
            if edit_distance(word, entry) == 1:
                suggestions.append(entry)
        return suggestions
    
    def replace_word(self, event):
        index = self.suggestions_display.index("@%s,%s" % (event.x, event.y))
        line_number, _ = map(int, index.split('.'))
        line = self.suggestions_display.get(f"{line_number}.0", f"{line_number}.end")
        selected_word = line.strip().split(":")[1].strip().split(",")[0]
        if selected_word:
            self.text_editor.tag_config("highlight", background="yellow")
            start_pos = self.text_editor.search(line.strip().split(":")[0], "1.0", "end", count=1)
            end_pos = f"{start_pos}+{len(line.strip().split(':')[0])}c"
            self.text_editor.tag_add("highlight", start_pos, end_pos)
            self.text_editor.tag_remove("highlight", "1.0", "end")
            self.text_editor.delete(start_pos, end_pos)
            self.text_editor.insert(start_pos, selected_word)

    def undo(self):
        self.text_editor.edit_undo()

if __name__ == "__main__":
    app = SpellingCheckerApp()
    app.mainloop()

# The first suggested word is automatically used to replace the incorrect word
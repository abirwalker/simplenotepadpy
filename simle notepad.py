import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from spellchecker import SpellChecker

# --- Setup ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x600")
app.title("Simple Notepad")
app.option_add("*tearOff", False)
app.configure(highlightthickness=0)


font_size = 14
dark_mode = False
spell = SpellChecker()
ignored_words = set()

# --- Text Area ---
text_area = ctk.CTkTextbox(app, font=("Consolas", font_size), wrap="word", undo=True)
text_area.pack(fill="both", expand=True, padx=10, pady=10)


# --- Update Title with Word Count ---
def update_title():
    words = len(text_area.get("1.0", "end-1c").split())
    app.title(f"Simple Notepad - {words} words")

# --- Spell Check ---
def check_spelling():
    text_area.tag_remove("misspelled", "1.0", "end")
    text = text_area.get("1.0", "end-1c")
    words = text.split()
    for word in set(words):
        if not spell.known([word]) and word.isalpha() and word not in ignored_words:
            start = "1.0"
            while True:
                start = text_area.search(word, start, stopindex="end")
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                text_area.tag_add("misspelled", start, end)
                start = end
    text_area.tag_config("misspelled", underline=True, foreground="red")

# --- HIghlight to ignore---
def on_right_click(event):
    text_area.bind("<Button-3>", on_right_click)  # Right click
    try:
        # Get mouse position index
        index = text_area.index(f"@{event.x},{event.y}")
        word_start = text_area.search(r"\m\w+", index, backwards=True, regexp=True)
        word_end = text_area.search(r"\M", index, regexp=True)

        if not word_start or not word_end:
            return

        word = text_area.get(word_start, word_end)

        # If word is tagged as misspelled, show context menu
        if "misspelled" in text_area.tag_names(word_start):
            def ignore_word():
                ignored_words.add(word)
                check_spelling()

            context = tk.Menu(app, tearoff=0)
            context.add_command(label=f"Ignore '{word}'", command=ignore_word)
            context.tk_popup(event.x_root, event.y_root)
    except:
        pass
text_area.bind("<Button-3>", on_right_click)

def on_typing(event=None):
    update_title()
    check_spelling()

text_area.bind("<KeyRelease>", on_typing)

# --- Ignore ---
def add_to_ignore():
    def confirm_ignore(event=None):
        word = entry.get().strip()
        if word:
            ignored_words.add(word)
            check_spelling()
        popup.destroy()

    popup = ctk.CTkToplevel(app)
    popup.title("Ignore Word")
    popup.geometry("300x120")
    popup.grab_set()

    ctk.CTkLabel(popup, text="Enter word to ignore:").pack(pady=10)
    entry = ctk.CTkEntry(popup, width=250)
    entry.pack(pady=5)
    entry.focus()

    btn = ctk.CTkButton(popup, text="Ignore", command=confirm_ignore)
    btn.pack(pady=5)

    entry.bind("<Return>", confirm_ignore)

# --- File Actions ---
def new_file():
    text_area.delete("1.0", "end")
    update_title()

def open_file():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, "r") as f:
            text_area.delete("1.0", "end")
            text_area.insert("1.0", f.read())
        update_title()

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, "w") as f:
            f.write(text_area.get("1.0", "end-1c"))

def exit_app():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        app.destroy()

# --- Edit Actions ---
def undo_action():
    try: text_area.edit_undo()
    except: pass

def redo_action():
    try: text_area.edit_redo()
    except: pass

def cut_action(): text_area.event_generate("<<Cut>>")
def copy_action(): text_area.event_generate("<<Copy>>")
def paste_action(): text_area.event_generate("<<Paste>>")

# --- Find & Replace ---
def highlight_all(keyword):
    text_area.tag_remove("highlight", "1.0", "end")
    if keyword:
        start = "1.0"
        while True:
            start = text_area.search(keyword, start, nocase=True, stopindex="end")
            if not start: break
            end = f"{start}+{len(keyword)}c"
            text_area.tag_add("highlight", start, end)
            start = end
    text_area.tag_config("highlight", background="yellow", foreground="black")

def find_replace():
    popup = ctk.CTkToplevel(app)
    popup.title("Find & Replace")
    popup.geometry("320x205")
    popup.grab_set()
    popup.focus_set()

    ctk.CTkLabel(popup, text="Find:").pack(pady=(10, 0))
    find_entry = ctk.CTkEntry(popup, width=280)
    find_entry.pack(pady=5)
    find_entry.focus()

    ctk.CTkLabel(popup, text="Replace with:").pack(pady=(10, 0))
    replace_entry = ctk.CTkEntry(popup, width=280)
    replace_entry.pack(pady=5)

    def do_replace(event=None):
        keyword = find_entry.get()
        replacement = replace_entry.get()
        if keyword:
            content = text_area.get("1.0", "end-1c")
            new_content = content.replace(keyword, replacement)
            text_area.delete("1.0", "end")
            text_area.insert("1.0", new_content)
            highlight_all(keyword)
            update_title()
        popup.destroy()

    replace_btn = ctk.CTkButton(popup, text="Replace All", command=do_replace)
    replace_btn.pack(pady=10)

    find_entry.bind("<Return>", do_replace)
    replace_entry.bind("<Return>", do_replace)

# --- Font Size ---
def set_font_size(size):
    global font_size
    font_size = size
    text_area.configure(font=("Consolas", font_size))

# --- View ---
def zoom_in(): set_font_size(font_size + 2)
def zoom_out(): set_font_size(max(8, font_size - 2))
def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    mode = "dark" if dark_mode else "light"
    ctk.set_appearance_mode(mode)

    # Manually fix menu colors
    if dark_mode:
        bg = "#2b2b2b"  # Matches CTk dark bg
        fg = "#ffffff"
    else:
        bg = "#f0f0f0"
        fg = "#000000"

    menubar.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
    file_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
    edit_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
    view_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
    font_size_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)


text_area.bind("<Control-MouseWheel>", lambda e: zoom_in() if e.delta > 0 else zoom_out())

# --- Menu Bar ---
menubar = tk.Menu(app)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open...", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=file_menu)

edit_menu = tk.Menu(menubar, tearoff=0)
edit_menu.add_command(label="Undo", command=undo_action)
edit_menu.add_command(label="Redo", command=redo_action)
edit_menu.add_separator()
edit_menu.add_command(label="Cut", command=cut_action)
edit_menu.add_command(label="Copy", command=copy_action)
edit_menu.add_command(label="Paste", command=paste_action)
edit_menu.add_separator()
edit_menu.add_command(label="Find & Replace", command=find_replace)
edit_menu.add_command(label="Ignore Word...", command=add_to_ignore)

menubar.add_cascade(label="Edit", menu=edit_menu)

view_menu = tk.Menu(menubar, tearoff=0)
view_menu.add_command(label="Zoom In", command=zoom_in)
view_menu.add_command(label="Zoom Out", command=zoom_out)

font_size_menu = tk.Menu(view_menu, tearoff=0)
for size in [10, 12, 14, 16, 18, 20, 24]:
    font_size_menu.add_command(label=str(size), command=lambda s=size: set_font_size(s))
view_menu.add_cascade(label="Font Size", menu=font_size_menu)

view_menu.add_separator()
view_menu.add_command(label="Toggle Dark/Light Mode", command=toggle_mode)
menubar.add_cascade(label="View", menu=view_menu)

# Initial menu theme based on current mode
bg = "#f0f0f0" if not dark_mode else "#2b2b2b"
fg = "#000000" if not dark_mode else "#ffffff"
menubar.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
file_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
edit_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
view_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
font_size_menu.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

app.config(menu=menubar)

# --- Start ---
set_font_size(font_size)
app.mainloop()
# --- End ---

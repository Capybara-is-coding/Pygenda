import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

tasks = []
current_theme = "Pyneapple"

# Dictionary of various color themes.
themes = {
    "Pyneapple": {"bg": "#FFE079", "fg": "#FFA000", "button_bg": "#FFB400", "button_fg": "white"},
    "ChocoPy": {"bg": "#C1956C", "fg": "#654D47", "button_bg": "#EADFBF", "button_fg": "#723020"},
    "Strawberry": {"bg": "#FF82AB", "fg": "#520113", "button_bg": "#C31458", "button_fg": "#FFE0E8"},
    "Blueberry": {"bg": "#DDB9D5", "fg": "#706A9E", "button_bg": "#D57E90", "button_fg": "white"},
}

# Available fonts
fonts = ["Helvetica", "Consolas", "Segoe UI", "Ink Free"]

app = tk.Tk()
app.title('Pygenda')
app.geometry('400x600')
current_font = tk.StringVar(value="Helvetica")


def apply_theme(theme_name):
    '''Apply the selected theme and save the settings.'''
    global current_theme
    current_theme = theme_name  
    theme = themes[theme_name]

    app.config(bg=theme["bg"])
    title_label.config(bg=theme["bg"], fg=theme["fg"])
    time_label.config(bg=theme["bg"], fg=theme["fg"])
    task_entry.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
    add_button.config(bg=theme["button_bg"], fg=theme["button_fg"])
    remove_button.config(bg=theme["button_bg"], fg=theme["button_fg"])
    tasks_frame.config(bg=theme["bg"])

    for task_text, task_var, check, remove_btn, _ in tasks:
        check.config(
            bg=scrollable_frame.cget("bg"),
            fg="gray" if task_var.get() else theme["fg"],
            font=(current_font.get(), 12, 'italic' if task_var.get() else 'normal')
        )
        remove_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])

    save_settings()  # Save immediately after switching themes.
    
    
def get_fixed_width():
    '''Calculate the appropriate Checkbutton width.'''
    return 26  # Make sure the `Delete` button is not squeezed by the task text.


def apply_font():
    '''
    Apply the selected font and update the task UI.
    '''
    font_name = current_font.get()
    title_label.config(font=(font_name, 18, 'bold'))
    time_label.config(font=(font_name, 14))
    task_entry.config(font=(font_name, 14))
    add_button.config(font=(font_name, 12))
    remove_button.config(font=(font_name, 12))
    font_dropdown.config(font=(font_name, 12))
    theme_dropdown.config(font=(font_name, 12))

    for _, _, check, remove_btn, task_frame in tasks:
        check.config(font=(font_name, 12), width=get_fixed_width())  # Recalculate Width.
        remove_btn.config(font=(font_name, 10))
        task_frame.grid(sticky="ew", padx=5, pady=2, columnspan=2)  # Re-adjust the task frame to prevent misalignment.

    save_settings()  # Save immediately after selecting the font.


def add_task():
    '''
    Add a task to the task list and display it in the task frame.
    '''
    task_text = task_entry.get().strip()
    if not task_text:
        messagebox.showwarning('Warning', 'Task cannot be empty!')
        return

    task_var = tk.BooleanVar()
    task_var.set(False)

    # The task box fills the white area.
    task_frame = tk.Frame(scrollable_frame, bg="white")
    task_frame.grid(sticky="ew", padx=5, pady=2, columnspan=2)  # Make sure `task_frame` takes up the entire area.
    task_frame.columnconfigure(0, weight=1)  # Task text fills the left side.
    task_frame.columnconfigure(1, weight=0)  # 'Delete' fills the left side.

    task_check = tk.Checkbutton(
        task_frame,
        text=task_text,
        font=(current_font.get(), 12),
        variable=task_var,
        onvalue=True,
        offvalue=False,
        anchor="w",
        width=get_fixed_width(),  # Make the Checkbutton width fixed.
        bg="white",
        fg=themes[current_theme]["fg"],
        selectcolor="white",
        command=lambda: mark_task_complete(task_var, task_check)
    )
    task_check.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=2)

    # Delete button fixed on the right side.
    remove_btn = tk.Button(
        task_frame,
        text="Delete",
        font=(current_font.get(), 10),
        bg=themes[current_theme]["button_bg"],
        fg=themes[current_theme]["button_fg"]
    )
    remove_btn.config(command=lambda: remove_task(task_text, task_frame))
    remove_btn.grid(row=0, column=1, sticky="e", padx=(5, 10), pady=2)

    # Save to Task List.
    tasks.append((task_text, task_var, task_check, remove_btn, task_frame))  
    task_entry.delete(0, 'end')  
    save_tasks()

    # Ensure scrollbars are updated.
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def mark_task_complete(task_var, task_check):
    '''
    Mark a task as completed or incomplete.
    '''
    if task_var.get(): # When the task is completed, the text turns gray and Italic.
        task_check.config(
            fg="gray",
            font=(current_font.get(), 12, 'italic') 
        )
    else: # If not completed, restore the original theme color and cancel italics.
        task_check.config(
            fg=themes[current_theme]["fg"],
            font=(current_font.get(), 12, 'normal')
        )


def remove_completed_tasks():
    '''
    Remove all completed tasks from the list.
    '''
    global tasks
    new_tasks = []

    for task_text, task_var, task_check, remove_btn, task_frame in tasks:
        if task_var.get():  # The task is completed (Checkbutton is checked).
            task_frame.destroy()  # Delete the entire task box.
        else:
            new_tasks.append((task_text, task_var, task_check, remove_btn, task_frame))

    tasks = new_tasks  # Only keep unfinished tasks.
    save_tasks()

    # Ensure scrollbars are updated.
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def remove_task(task_text, task_frame):
    '''
    Remove a specific task from the task list and UI.
    '''
    global tasks
    tasks = [task for task in tasks if task[0] != task_text]  

    if task_frame.winfo_exists():
        task_frame.destroy()  # Delete the entire task box.

    save_tasks()



def save_tasks():
    '''Save the task list to a JSON file.'''
    with open("tasks.json", "w", encoding="utf-8") as file:
        json.dump([t[0] for t in tasks], file, ensure_ascii=False, indent=4)



tasks_frame = tk.Frame(app, bg="white", width=350, height=250)
tasks_frame.columnconfigure(0, weight=1)
tasks_frame.columnconfigure(1, weight=0)

canvas = tk.Canvas(tasks_frame, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(tasks_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))  # Automatically adjust scroll range.
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")



# Let the mouse wheel scroll Canvas
def _on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)


def add_task_from_load(task_text):
    '''
    Load tasks from JSON and add them to UI.
    '''
    task_var = tk.BooleanVar()
    task_var.set(False)

    task_frame = tk.Frame(scrollable_frame, bg="white")
    task_frame.grid(sticky="ew", padx=5, pady=2, columnspan=2)
    task_frame.columnconfigure(0, weight=1)
    task_frame.columnconfigure(1, weight=0)

    task_check = tk.Checkbutton(
        task_frame,
        text=task_text,
        font=(current_font.get(), 12),
        variable=task_var,
        onvalue=True,
        offvalue=False,
        anchor="w",
        width=get_fixed_width(),
        bg="white",
        fg=themes[current_theme]["fg"],
        selectcolor="white",
        command=lambda: mark_task_complete(task_var, task_check)
    )
    task_check.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=2)

    remove_btn = tk.Button(
        task_frame,
        text="Delete",
        font=(current_font.get(), 10),
        bg=themes[current_theme]["button_bg"],
        fg=themes[current_theme]["button_fg"]
    )
    remove_btn.config(command=lambda: remove_task(task_text, task_frame))
    remove_btn.grid(row=0, column=1, sticky="e", padx=(5, 10), pady=2)

    tasks.append((task_text, task_var, task_check, remove_btn, task_frame))

    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    
def load_tasks():
    '''Load tasks from a JSON file and restore the UI.'''
    global tasks

    # Ensure the UI is clear to prevent duplicate loading.
    for _, _, check, remove_btn, task_frame in tasks:
        task_frame.destroy()

    tasks.clear()  # Clear old tasks to prevent duplicate loading.

    # Reading tasks from JSON.
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r", encoding="utf-8") as file:
            try:
                saved_tasks = json.load(file)
                for task_text in saved_tasks:
                    add_task_from_load(task_text)  # Loading tasks one by one.
            except json.JSONDecodeError:
                print("⚠️ Failed to read task file.")


def load_theme():
    '''Load theme from JSON file and apply. '''
    global current_theme

    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if "theme" in data:
                    current_theme = data["theme"]
            except json.JSONDecodeError:
                print("⚠️ settings.json - Failed to load, using default theme")

    apply_theme(current_theme)
    
    
def load_settings():
    '''Loading themes and fonts from JSON files.'''
    global current_theme

    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if "theme" in data:
                    current_theme = data["theme"]
                if "font" in data:
                    current_font.set(data["font"])
            except json.JSONDecodeError:
                print("⚠️ settings.json - Failed to load, using default theme and fonts")

    apply_theme(current_theme)
    apply_font()


def refresh_task_area():
    '''Refresh the task area after the task is loaded.'''
    tasks_frame.update_idletasks()  # Force Tkinter to update the UI to prevent the size error after restart.

load_tasks()
refresh_task_area()


def update_time():
    '''Displays the current time and updates every second.'''
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    time_label.config(text=current_time)
    time_label.after(1000, update_time)


def change_theme(selected_theme):
    
    apply_theme(selected_theme)
    save_theme()
    
    
def save_theme():
    '''Save current theme to JSON file.'''
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump({"theme": current_theme}, file)
        
        
def save_settings():
    '''Save current theme and fonts to JSON file.'''
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump({"theme": current_theme, "font": current_font.get()}, file, ensure_ascii=False, indent=4)
    
    
    
title_label = tk.Label(app, text='To-Do List', font=('Helvetica', 18, 'bold'))
task_entry = tk.Entry(app, font=('Helvetica', 14))
task_entry.bind("<Return>", lambda event: add_task()) # Press Enter to add a task directly.
add_button = tk.Button(app, text='Add Task', font=('Helvetica', 12), command=add_task)
remove_button = tk.Button(app, text='Remove Completed Tasks', font=('Helvetica', 12), command=remove_completed_tasks)

title_label.pack(pady=10)

task_entry.pack(pady=10, padx=20, fill="x")
add_button.pack(pady=5) 
remove_button.pack(pady=5)

time_label = tk.Label(
    app,
    font=('Helvetica', 16, 'bold'),
    anchor="center",
    justify="center",
    width=30,  
    height=2,  
    padx=10,  
    pady=5,
    bg=themes[current_theme]["bg"],
    fg=themes[current_theme]["fg"]
)
time_label.pack(after=remove_button, pady=(5, 5))

tasks_frame.pack(pady=10, padx=10)
tasks_frame.pack_propagate(False)

# Theme selection drop-down menu
theme_var = tk.StringVar(value="Pyneapple")  # Store the currently selected topic
theme_dropdown = tk.OptionMenu(app, theme_var, *themes.keys(), command=change_theme)
theme_dropdown.config(font=('Helvetica', 12))
theme_dropdown.pack(side="left", padx=10, pady=10, anchor="s")

# Font selection drop-down menu
font_dropdown = tk.OptionMenu(app, current_font, *fonts, command=lambda _: apply_font())
font_dropdown.config(font=('Helvetica', 12))
font_dropdown.pack(side="right", padx=10, pady=10, anchor="s")


update_time()
load_settings()
apply_theme(current_theme)
apply_font()
load_tasks()
refresh_task_area()

app.mainloop()
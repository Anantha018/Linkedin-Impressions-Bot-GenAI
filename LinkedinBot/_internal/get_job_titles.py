import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from groq import Groq
import ttkbootstrap as ttkb
from linkedin_bot import LinkedInBot
from job_titles import JobTitleExtractor
import sys

class LinkedInBotGUI:
    def __init__(self):
        self.bot = LinkedInBot()
        self.titles_dict = {}
        self.client = Groq(api_key="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")
        self.job_title_extractor = JobTitleExtractor(self.client)

        self.root = ttkb.Window(themename="darkly")
        self.root.title("LinkedIn Bot")
        self.root.state('zoomed')

        self.style = ttkb.Style()
        self.style.configure("TLabel", font=("Roboto", 12))
        self.style.configure("TButton", font=("Roboto", 12))

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.frame1 = ttk.Frame(self.main_frame)
        self.frame2 = ttk.Frame(self.main_frame)

        self.frame1.grid(row=0, column=0, sticky="nsew")
        self.frame2.grid(row=0, column=0, sticky="nsew")

        self.setup_frame1()
        self.setup_frame2()

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.frame1.grid_rowconfigure(8, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame2.grid_rowconfigure(2, weight=1)
        self.frame2.grid_columnconfigure(0, weight=1)

        self.show_frame(self.frame1)

    def setup_frame1(self):
        label = ttk.Label(self.frame1, text="Use AI to generate relevant job titles for your post content: (optional) \n\n Paste your LinkedIn post content here:", style="TLabel")
        label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.entry = tk.Text(self.frame1, wrap="word", height=10, width=60, font=("Roboto", 10))
        self.entry.grid(row=1, column=0, padx=5, pady=(0, 20), sticky="nsew")

        button = ttk.Button(self.frame1, text="Get Job Titles", command=self.trigger_get_job_titles, style="success.TButton")
        button.grid(row=2, column=0, pady=(0, 20), columnspan=2)

        result_label = ttk.Label(self.frame1, text="Job Titles:", style="TLabel")
        result_label.grid(row=3, column=0, pady=(20, 10), sticky="w")

        self.result = tk.Text(self.frame1, wrap="word", height=5, width=60, font=("Roboto", 10), state="disabled")
        self.result.grid(row=4, column=0, padx=5, pady=(0, 20), sticky="nsew")

        dict_frame = ttk.Frame(self.frame1)
        dict_frame.grid(row=5, column=0, pady=(20, 0), sticky="nsew")

        title_label = ttk.Label(dict_frame, text="Title:", style="TLabel")
        title_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.title_entry = ttk.Entry(dict_frame)
        self.title_entry.grid(row=0, column=1, padx=(0, 20), sticky="w")

        count_label = ttk.Label(dict_frame, text="Count:", style="TLabel")
        count_label.grid(row=0, column=2, padx=(0, 10), sticky="w")

        self.count_entry = ttk.Entry(dict_frame)
        self.count_entry.grid(row=0, column=3, sticky="w")

        add_button = ttk.Button(dict_frame, text="Add/Update", command=self.add_or_update_dict, style="success.TButton")
        add_button.grid(row=0, column=4, padx=(20, 0), sticky="w")

        self.treeview = ttk.Treeview(self.frame1, columns=("Title", "Count"), show="headings", selectmode="browse")
        self.treeview.heading("Title", text="Job Title")
        self.treeview.heading("Count", text="Number of Profile Visits")
        self.treeview.column("Title", width=200, anchor="w")
        self.treeview.column("Count", width=100, anchor="e")
        self.treeview.grid(row=6, column=0, pady=10, sticky="nsew")
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)

        button_frame = ttk.Frame(self.frame1)
        button_frame.grid(row=7, column=0, pady=(10, 20), sticky="nsew")

        remove_button = ttk.Button(button_frame, text="Remove Selected Entry", command=self.remove_entry, style="danger.TButton")
        remove_button.grid(row=0, column=0, padx=(0, 10), ipadx=5, ipady=5, sticky="nsew")

        send_button = ttk.Button(button_frame, text="Add to list", command=self.send_to_linkedin_bot, style="success.TButton")
        send_button.grid(row=0, column=1, padx=(10, 0), ipadx=5, ipady=5, columnspan=2)

        self.checkbox_var1 = tk.IntVar()
        self.checkbox_var2 = tk.IntVar()

        checkbox1 = ttk.Checkbutton(button_frame, text="Visit only your connections", variable=self.checkbox_var1)
        checkbox2 = ttk.Checkbutton(button_frame, text="Visit only the entered job titles", variable=self.checkbox_var2)

        checkbox1.grid(row=0, column=5, padx=(15, 10), pady=(0, 0))
        checkbox2.grid(row=0, column=6, padx=(15, 10), pady=(0, 0))

        next_button = ttk.Button(self.frame1, text="Next", command=self.validate_checkboxes, style="primary.TButton")
        next_button.grid(row=7, column=0, pady=(10,0), sticky="se")

    def setup_frame2(self):
        chrome_image = Image.open(self.resource_path("Images/linkedin_page_window2.png"))
        chrome_image = chrome_image.resize((600, 400), Image.LANCZOS)
        self.chrome_window_image = ImageTk.PhotoImage(chrome_image)

        chrome_window_image_label = tk.Label(self.frame2, image=self.chrome_window_image)
        chrome_window_image_label.grid(row=0, column=0, pady=10, sticky='n')

        chrome_text = '''Important note:- \n
1) Ensure the LinkedIn Chrome window remains active and open while the automation is in progress. \n 
2) Make sure no other activities are performed during the automation, and ensure the screen does not time out during the process. Ensure that only the Chrome window opened by the terminal command is displayed, and no other applications are launched.\n
3) If you want to quit the automation or stop the bot, simply close the Chrome window. And when there is no automation activity on the screen, it means that the automation has been completed successfully.\n

=> To prevent your screen from timing out or going to sleep during the automation, follow these instructions:

-- Windows: Go to Settings > System > Power & sleep. Set both "When plugged in, turn off after" and "PC goes to sleep after" to Never.

-- Mac (macOS): Go to System Preferences > Energy Saver and set "Turn display off after" to Never. Check "Prevent computer from sleeping automatically when the display is off".

-- Linux: For GNOME: Go to Settings > Power and set "Blank screen" to Never.\n
          For KDE: Go to System Settings > Power Management and set the display to Never turn off.
'''

        chrome_window_label = ttk.Label(self.frame2, text=chrome_text, style="TLabel")
        chrome_window_label.grid(row=1, column=0, pady=20)

        start_bot_button = ttk.Button(self.frame2, text="Start the bot", command=self.trigger_which_function, style="success.TButton")
        start_bot_button.grid(row=10, column=0, pady=(10, 20), sticky="s")

        back_button = ttk.Button(self.frame2, text="Back", command=lambda: self.show_frame(self.frame1), style="primary.TButton")
        back_button.grid(row=10, column=0, pady=(10, 20), sticky="w")

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def trigger_get_job_titles(self):
        user_input = self.entry.get("1.0", "end").strip()
        try:
            job_titles = self.job_title_extractor.get_job_titles(user_input)
            formatted_job_titles = ', '.join(job_titles.split('\n'))
            self.result.config(state="normal")
            self.result.delete("1.0", "end")
            self.result.insert("end", formatted_job_titles)
            self.result.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_or_update_dict(self):
        title = self.title_entry.get().strip()
        count = self.count_entry.get().strip()
        if title and count.isdigit():
            count = int(count)
            if count >= 10:
                self.titles_dict[title] = count
                self.update_treeview()
                self.title_entry.delete(0, "end")
                self.count_entry.delete(0, "end")
            else:
                messagebox.showwarning("Invalid Count", "Count must be at least 10 to be added.")
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid title and count.")

    def update_treeview(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for title, count in self.titles_dict.items():
            self.treeview.insert("", "end", values=(title, count))

    def on_treeview_select(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            title, count = self.treeview.item(selected_item, "values")
            self.title_entry.delete(0, "end")
            self.count_entry.delete(0, "end")
            self.title_entry.insert(0, title)
            self.count_entry.insert(0, count)

    def remove_entry(self):
        selected_item = self.treeview.selection()
        if selected_item:
            title, count = self.treeview.item(selected_item, "values")
            del self.titles_dict[title]
            self.treeview.delete(selected_item)
            self.title_entry.delete(0, "end")
            self.count_entry.delete(0, "end")
        else:
            messagebox.showwarning("No Selection", "Please select an entry to remove.")

    def send_to_linkedin_bot(self):
        if self.titles_dict:
            print("Sending the following data to LinkedIn bot:")
            for title, count in self.titles_dict.items():
                print(f"Title: {title}, Count: {count}")
            messagebox.showinfo("Data Sent", "The data has been successfully sent to the LinkedIn bot.")
        else:
            messagebox.showwarning("No Data", "No data to send. Please add titles and counts first.")

    def trigger_which_function(self):
        self.root.quit()
        self.root.destroy()
        
        if self.checkbox_var1.get():
            self.bot.go_to_connections_page()
        
        if self.checkbox_var2.get():
            self.bot.search_user_entered_job_titles(self.titles_dict)
        
        if self.checkbox_var1.get() and self.checkbox_var2.get():
            self.bot.go_to_connections_page()
            self.bot.search_user_entered_job_titles(self.titles_dict)

    def show_frame(self, frame):
        frame.tkraise()

    def validate_checkboxes(self):
        if self.checkbox_var1.get() == 0 and self.checkbox_var2.get() == 0:
            messagebox.showwarning("Selection Required", "Please select at least one option.")
        elif self.checkbox_var2.get() == 1 and not self.titles_dict:
            messagebox.showwarning("List Required", "Please ensure the list of job titles is not empty when the second option is selected.")
        else:
            self.show_frame(self.frame2)


    def run(self):
        self.root.mainloop()

# Usage
if __name__ == "__main__":
    app = LinkedInBotGUI()
    app.run()
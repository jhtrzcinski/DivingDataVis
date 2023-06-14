import tkinter as tk
from tkinter import messagebox
from openpyxl import Workbook

# Initialize Workbook
wb = Workbook()
ws = wb.active

# Column headers
headers = ['Name', 'Board', 'Dive', 'Score', 'Low', 'High', 'Goal']
ws.append(headers)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('DivingBoard')

        self.name_var = tk.StringVar()
        self.dive_var = tk.StringVar()
        self.board_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.low_var = tk.StringVar()
        self.high_var = tk.StringVar()
        self.goal_var = tk.StringVar()

        # Store all name buttons
        self.name_buttons = {}
        self.dive_buttons = {}

        # Frames for the buttons
        self.name_frame = tk.Frame(self)
        self.name_frame.grid(row = 8,column = 0)
        self.dive_frame = tk.Frame(self)
        self.dive_frame.grid(row = 8,column = 1)

        # Diver's name entry
        name_label = tk.Label(self, text='Name')
        name_label.grid(row = 0, column = 0)
        name_entry = tk.Entry(self, textvariable=self.name_var)
        name_entry.grid(row = 0, column = 1)

        # Dive number entry
        dive_label = tk.Label(self, text='Dive')
        dive_label.grid(row = 1, column = 0)
        dive_entry = tk.Entry(self, textvariable=self.dive_var)
        dive_entry.grid(row = 1, column = 1)

        # Board toggle
        board_label = tk.Label(self, text='Board')
        board_label.grid(row=2, column=0)
        board_button_1m = tk.Radiobutton(self, text='1m', variable=self.board_var, value='1')
        board_button_1m.grid(row=2, column=1)
        board_button_3m = tk.Radiobutton(self, text='3m', variable=self.board_var, value='3')
        board_button_3m.grid(row=2, column=2)

        # Score, High, Low, and Goal entries
        score_label = tk.Label(self, text='Score')
        score_label.grid(row=3, column=0)
        score_entry = tk.Entry(self, textvariable=self.score_var)
        score_entry.grid(row=3, column=1)

        low_label = tk.Label(self, text='Low')
        low_label.grid(row=4, column=0)
        low_entry = tk.Entry(self, textvariable=self.low_var)
        low_entry.grid(row=4, column=1)

        high_label = tk.Label(self, text='High')
        high_label.grid(row=5, column=0)
        high_entry = tk.Entry(self, textvariable=self.high_var)
        high_entry.grid(row=5, column=1)

        goal_label = tk.Label(self, text='Goal')
        goal_label.grid(row=6, column=0)
        goal_entry = tk.Entry(self, textvariable=self.goal_var)
        goal_entry.grid(row=6, column=1)

        # Done button
        done_button = tk.Button(self, text='Done', command=self.add_to_excel)
        done_button.grid(row=7, column=0, columnspan=2)

    def add_to_excel(self):
        name = self.name_var.get()
        if name not in self.name_buttons:
            # Create a new button for this name
            new_button = tk.Button(self.name_frame, text=name, command=lambda: self.name_var.set(name))
            new_button.pack()
            self.name_buttons[name] = new_button

        dive = self.dive_var.get()
        if dive not in self.dive_buttons:
            # Create a new button for this dive
            new_dive_button = tk.Button(self.dive_frame, text=dive, command=lambda: self.dive_var.set(dive))
            new_dive_button.pack()
            self.dive_buttons[dive] = new_dive_button

        row_data = [self.name_var.get(), self.board_var.get(), self.dive_var.get(), self.score_var.get(),
                    self.low_var.get(), self.high_var.get(), self.goal_var.get()]
        ws.append(row_data)
        wb.save('DiveData.xlsx')  # save data to file
        self.clear_form()  # clear the form

    def clear_form(self):
        self.name_var.set('')
        self.dive_var.set('')
        self.board_var.set('')
        self.score_var.set('')
        self.low_var.set('')
        self.high_var.set('')
        self.goal_var.set('')


if __name__ == "__main__":
    app = Application()
    app.mainloop()

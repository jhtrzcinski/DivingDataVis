import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from openpyxl import Workbook
from openpyxl.drawing.image import Image

filename = ""

def browseFiles():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select a file", 
    filetypes = (("Comma-separated files", "*.csv*"), ("Excel files", "*.xlsx*"), ("all files", "*.*")))
    label_file_explorer.configure(text="File Opened: " + filename)

def buttonClicked():
    global filename
    output_name = output_name_entry.get()

    if filename:
        window.destroy()
        main(filename, output_name)

def main(input_file, output_name):
    # determine file type
    _, file_extension = os.path.splitext(input_file)

    # read data
    if '.csv' == file_extension:
        data = pd.read_csv(input_file, skiprows=1, names=['name', 'board', 'dive', 'score', 'low', 'high', 'goal'])
    elif '.xlsx' == file_extension:
        data = pd.read_excel(input_file, skiprows=1, names=['name', 'board', 'dive', 'score', 'low', 'high', 'goal'])
    else:
        root = Tk()
        root.withdraw()
        user_response = messagebox.askokcancel("Information","File type not supported, please choose a \'.xlsx\', or a \'.csv\' file.")
        root.destroy()
        return

    # Create mapping and its inverse
    datamap = {'balk':0, 'fail':0.5, 'triple bogey':1, 'double bogey':2, 'bogey':3, 'par':4, 'birdie':5, 'eagle':6}
    inverse_datamap = {v: k for k, v in datamap.items()}

    # If either 'score' or 'goal' column is missing, generate it
    data.loc[data['score'].isnull(), 'score'] = data['goal'].map(datamap)
    data.loc[data['goal'].isnull(), 'goal'] = data['score'].map(inverse_datamap)

    data.sort_values(by=['name', 'board', 'dive'], inplace=True)

    UniqueNames = data.name.unique()

    DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}

    for key in DataFrameDict.keys():
        DataFrameDict[key] = data[:][data.name == key]

    # create folders for each diver and save graphs
    output_folder = str(output_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    wb = Workbook()
    
    for name, df in DataFrameDict.items():
        diver_folder = os.path.join(output_folder, name.replace(" ", "_"))
        if not os.path.exists(diver_folder):
            os.makedirs(diver_folder)

        unique_dive_numbers = df.dive.unique()
        for dive_number in unique_dive_numbers:
            dive_df = df[df.dive == dive_number].copy()

            dive_df['MappedGoal'] = dive_df['goal'].map(datamap)

            plt.figure(figsize=(12, 6))
            graph = sns.lineplot(data=dive_df, x=range(len(dive_df)), y='MappedGoal', hue='board', marker='o', markersize=8, linestyle='-')
            plt.title(f"Dive Performance Over Time for {name} (Dive Number: {dive_number})")
            plt.xlabel("Chronological Dive Index")
            plt.ylabel("Goal")
            plt.legend(title='Board', loc='upper left')
            plt.tight_layout()

            # Set the y-axis labels from numbers to corresponding text
            labels_dict = datamap
            plt.yticks(list(labels_dict.values()), list(labels_dict.keys()))

            plt.savefig(os.path.join(diver_folder, f"DiveNumber_{dive_number}.png"))
            plt.close()

        # Excel file output
        ws = wb.create_sheet(name.replace(" ", "_")) # Create a sheet for each diver
        for i, dive_number in enumerate(unique_dive_numbers, start=1):
            img = Image(os.path.join(diver_folder, f"DiveNumber_{dive_number}.png")) # Load image
            img.width = 600
            img.height = 300
            ws.column_dimensions[chr(65 + i)].width = img.width // 6 # Adjust the column width
            ws.row_dimensions[i].height = img.height // 1.5 # Adjust the row height
            ws.add_image(img, f'{chr(65 + i)}1') # Add image to sheet

    wb.save(os.path.join(output_folder, "DiversGraphs.xlsx")) # Save the workbook

    root = Tk()
    root.withdraw()
    user_response = messagebox.askokcancel("Information","Data has been visualized. Click OK to open the file in explorer")

    if user_response:
        os.startfile(output_name)

    root.destroy()

if __name__ == '__main__':
    window = Tk()
    window.title('DivingBoard')
    window.geometry("700x350")
    window.config(background="gray")

    # Configure the grid
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=1)
    window.grid_rowconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)

    label_file_explorer = Label(window, text = "Press \'Browse Files\' to select a file", width = 100, fg = "Blue")
    label_output_name = Label(window, text = "Name output folder:", width = 20)
    button_explore = Button(window, text = "Browse Files", command = browseFiles)
    button_generate = Button(window, text="Generate", command=buttonClicked)
    output_name_entry = Entry(window, text = "Enter an output folder name", width= 50)

    label_file_explorer.grid(column = 0, row = 0, pady=10, sticky=W, columnspan=2)
    button_explore.grid(column = 2, row = 0, pady=10)

    label_output_name.grid(column = 0, row = 1, pady=10, sticky=W)
    output_name_entry.grid(column = 1, row = 1, pady=10, sticky=W)

    button_generate.grid(column = 1, row = 2, pady=10, sticky=E)

    window.mainloop()

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

filename = ""

def browseFiles():
        global filename
        filename = filedialog.askopenfilename(initialdir = "/",title = "Select a file", filetypes = (("Comma-seperated files", "*.csv*"), ("all files", "*.*")))
        label_file_explorer.configure(text="File Opened: " + filename)

def buttonClicked():
    global filename
    output_name = output_name_entry.get()

    if filename:
        window.destroy()
        main(filename, output_name)



def main(input_file, output_name):
    # read data
    data = pd.read_csv(input_file, skiprows=1, names=['number','DateTime','FirstName','LastName','ApparatusType','ApparatusHeight','DiveNumber','Grade','Angle'])
    data.drop('number', axis=1, inplace=True)

    # begin sorting it all
    data["FullName"] = data["LastName"] + ", " + data["FirstName"]
    data['DateTime'] = pd.to_datetime(data['DateTime'])
    data.sort_values(by=['FullName', 'ApparatusHeight', 'DiveNumber', 'DateTime'], inplace=True)

    data['Grade'].replace('', np.nan, inplace=True)
    data.dropna(subset=['Grade'], inplace=True)

    UniqueNames = data.FullName.unique()

    DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}

    for key in DataFrameDict.keys():
        DataFrameDict[key] = data[:][data.FullName == key]

    # create folders for each diver and save graphs

    output_folder = str(output_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for name, df in DataFrameDict.items():
        diver_folder = os.path.join(output_folder, name.replace(", ", "_"))
        if not os.path.exists(diver_folder):
            os.makedirs(diver_folder)

        unique_dive_numbers = df.DiveNumber.unique()
        for dive_number in unique_dive_numbers:
            datamap = {'balk':0, 'fail':0.5, 'triple bogey':1, 'double bogey':2, 'bogey':3, 'par':4, 'birdie':5, 'eagle':6}
            dive_df = df[df.DiveNumber == dive_number].copy()

            dive_df['MappedGrade'] = dive_df['Grade'].map(datamap)

            plt.figure(figsize=(12, 6))
            sns.lineplot(data=dive_df, x=range(len(dive_df)), y='MappedGrade', hue='ApparatusHeight', marker='o', markersize=8, linestyle='-')
            plt.title(f"Dive Performance Over Time for {name} (Dive Number: {dive_number})")
            plt.xlabel("Chronological Dive Index")
            plt.ylabel("Grade")
            plt.legend(title='Apparatus Height', loc='upper left')
            plt.tight_layout()
            plt.savefig(os.path.join(diver_folder, f"DiveNumber_{dive_number}.png"))
            plt.close()


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
    button_exit = Button(window, text="Exit", command=exit)
    button_generate = Button(window, text="Generate", command=buttonClicked)
    output_name_entry = Entry(window, text = "Enter an output folder name", width= 50)

    label_file_explorer.grid(column = 0, row = 0, pady=10, sticky=W, columnspan=2)
    button_explore.grid(column = 2, row = 0, pady=10)

    label_output_name.grid(column = 0, row = 1, pady=10, sticky=W)
    output_name_entry.grid(column = 1, row = 1, pady=10, sticky=W)

    button_generate.grid(column = 1, row = 2, pady=10, sticky=E)

    button_exit.grid(column = 2, row = 3, pady=10, sticky=E)

    window.mainloop()


# To Do: add output destination
#        Fix graphs so that they use the golf grading scale not 12345
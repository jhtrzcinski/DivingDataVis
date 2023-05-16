import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def main(input_file):
    # read data
    print("Reading CSV: " + str(input_file) + "\n")
    data = pd.read_csv(input_file, skiprows=1, names=['number','DateTime','FirstName','LastName','ApparatusType','ApparatusHeight','DiveNumber','Grade','Angle'])
    data.drop('number', axis=1, inplace=True)

    # begin sorting it all
    print("Cleaning up data... \n")
    data["FullName"] = data["LastName"] + ", " + data["FirstName"]
    data['DateTime'] = pd.to_datetime(data['DateTime'])
    data.sort_values(by=['FullName', 'ApparatusHeight', 'DiveNumber', 'DateTime'], inplace=True)

    data['Grade'].replace('', np.nan, inplace=True)
    data.dropna(subset=['Grade'], inplace=True)

    print("Finding Divers...\n")
    UniqueNames = data.FullName.unique()

    DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}

    for key in DataFrameDict.keys():
        DataFrameDict[key] = data[:][data.FullName == key]

    # create folders for each diver and save graphs
    print("Creating Folders...\n")
    output_folder = "DiverGraphs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Making graphs for each diver...\n")
    for name, df in DataFrameDict.items():
        diver_folder = os.path.join(output_folder, name.replace(", ", "_"))
        if not os.path.exists(diver_folder):
            os.makedirs(diver_folder)

        unique_dive_numbers = df.DiveNumber.unique()
        for dive_number in unique_dive_numbers:
            datamap = {'balk':0, 'fail':0.5, 'triple bogey':1, 'double bogey':2, 'bogey':3, 'par':4, 'birdie':5, 'eagle':6}
            dive_df = df[df.DiveNumber == dive_number]

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

    print("All done")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate dive performace graphs from a CSV file")
    parser.add_argument("input_file", help="Path to the input CSV file")
    args = parser.parse_args()

    input_file = args.input_file

    main(input_file)

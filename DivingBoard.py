import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import sys
import requests
import json

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

def read_license_file(file_path):
    try:
        with open(file_path, 'r') as license_file:
            license_data = json.load(license_file)
            return license_data
    except FileNotFoundError:
        return None

def verify_license_key(account_id, license_key, product_token):
    url = f"https://api.keygen.sh/v1/account/{account_id}/licenses/actions/validate-key"
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
        "Authorization": f"Bearer {product_token}"
        }
    payload = {"meta": {"key": license_key}}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

if __name__ == '__main__':
    pwd = os.path.dirname(os.path.realpath(__file__))
    license_file_path = os.path.join(pwd, 'license.json')

    parser = argparse.ArgumentParser(description="Generate dive performace graphs from a CSV file")
    parser.add_argument("input_file", help="Path to the input CSV file")
    args = parser.parse_args()

    input_file = args.input_file
    license_data = read_license_file(license_file_path)

    if license_data is None:
        print("Error: License information not found. Make sure license.json is in the same directory as DivingBoard.exe/")
        sys.exit(1)
    
    else:
        account_id = license_data["ACCOUNT_ID"]
        license_key = license_data["LICENSE_KEY"]
        product_token = license_data["PRODUCT_TOKEN"]

#    if not PRODUCT_TOKEN:
#        print("Error: KEYGEN_PRODUCT_TOKEN environment variable is not set.")
#        sys.exit(1)

    if verify_license_key(account_id, license_key, product_token):
        main(input_file)
    else:
        print("Invalid license key. Please provide a valid license key to use this program.")
        sys.exit(1)

    main(input_file)

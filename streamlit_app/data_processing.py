import os
import streamlit as st
import requests
import pandas as pd

# These values are read from secrets.toml in your app.py
BASE_URL = st.secrets["api"]["BASE_URL"]
API_TOKEN = st.secrets["api"]["API_TOKEN"]


def fetch_csv_from_api(database, year):
    """
    Fetches a CSV file for the given year from the specified database.
    It retrieves the list of available files from the API, then selects the
    one that has the specified year in its filename.
    """
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # Adjust the BASE_URL for the listing endpoint if BASE_URL includes '/data'
    # This splits off the '/data' part if present.
    base_root = BASE_URL.rsplit("/data", 1)[0]
    list_url = f"{base_root}/files"

    response = requests.get(list_url, headers=headers)
    if response.status_code != 200:
        st.error("Error fetching the file list from the API.")
        return pd.DataFrame()

    file_list = response.json().get("files", [])

    # Filter the files to those in the selected database and containing the year.
    matching_files = [
        f for f in file_list if f.startswith(f"{database}/") and f"{year}" in f
    ]

    if not matching_files:
        st.error(f"No CSV file found for year {year} in database '{database}'.")
        return pd.DataFrame()

    selected_file = matching_files[0]

    # Build the file URL.
    file_url = f"{BASE_URL}/{selected_file}"  # BASE_URL still includes '/data'
    file_response = requests.get(file_url, headers=headers)
    if file_response.status_code != 200:
        st.error(f"Failed to fetch '{selected_file}': {file_response.status_code}")
        return pd.DataFrame()

    local_file = f"/tmp/{os.path.basename(selected_file)}"
    with open(local_file, "wb") as f:
        f.write(file_response.content)

    if database == "BACI_HS92_V202501":
        return read_baci_data(local_file)
    elif database == "DataComex_output_with_metadata":
        return read_datacomex_data(local_file)


def read_baci_data(local_file):
    """
    Reads the BACI data from the API and returns it as a DataFrame.
    """
    data = pd.read_csv(local_file, index_col=0)
    data.pais = data.pais.astype(str).str.zfill(3)
    return data


def read_datacomex_data(local_file):
    """
    Reads the DataComex data from the API and returns it as a DataFrame.
    """
    data = pd.read_csv(local_file)
    data.pais = data.pais.astype(str).str.zfill(3)
    return data

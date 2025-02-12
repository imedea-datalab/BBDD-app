# app.py
import streamlit as st
import json
import requests
import pandas as pd
from io import StringIO

BASE_URL = st.secrets["api"]["BASE_URL"]
API_TOKEN = st.secrets["api"]["API_TOKEN"]

with open("options.json") as f:
    options = json.load(f)

st.title("Filtered Data Downloader")

folder_options = ["All"] + options.get("folders", [])
selected_folder = st.selectbox("Select Data Source:", folder_options)

st.sidebar.header("Filters")
flujos_filter = st.sidebar.multiselect("Select Flujo:", options["flujo"], default=options["flujo"][0])
años_filter = st.sidebar.multiselect("Select Año:", options["año"], default=options["año"][-1])
paises_filter = st.sidebar.multiselect("Select País:", options["pais_nombre"], default=options["pais_nombre"][0])

if st.sidebar.button("Apply Filters"):
    folders_to_process = options["folders"] if selected_folder == "All" else [selected_folder]
    filtered_datasets = []
    
    for folder in folders_to_process:
        try:
            # Fixed the API endpoint path
            response = requests.get(f"{BASE_URL}/data/{folder}/files", 
                                 headers={"Authorization": f"Bearer {API_TOKEN}"})  # Added token
            
            if response.status_code == 200 and "files" in response.json():
                folder_data = []
                files = response.json()["files"]
                
                for file in files:
                    try:
                        # Fixed the file request path
                        file_response = requests.get(
                            f"{BASE_URL}/data/{folder}/{file}",
                            headers={"Authorization": f"Bearer {API_TOKEN}"}  # Added token
                        )
                        if file_response.status_code == 200:
                            df = pd.read_csv(StringIO(file_response.text))
                            df['source_folder'] = folder
                            folder_data.append(df)
                    except Exception as e:
                        st.error(f"Error loading file {file} from {folder}: {str(e)}")
                
                if folder_data:
                    folder_df = pd.concat(folder_data, ignore_index=True)
                    
                    folder_filtered = folder_df[
                        (folder_df["flujo"].isin(flujos_filter)) & 
                        (folder_df["año"].isin(años_filter)) &
                        (folder_df["pais_nombre"].isin(paises_filter))
                    ]
                    
                    if not folder_filtered.empty:
                        filtered_datasets.append(folder_filtered)
                        
        except Exception as e:
            st.error(f"Error processing folder {folder}: {str(e)}")

    if filtered_datasets:
        final_data = pd.concat(filtered_datasets, ignore_index=True)
        
        st.write(f"Displaying {len(final_data)} rows of filtered data")
        st.dataframe(final_data)
        
        csv_data = final_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Filtered Data",
            csv_data,
            "filtered_data.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.warning("No data found matching the selected filters.")
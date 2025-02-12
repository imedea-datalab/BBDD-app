# app.py
import streamlit as st
import json
import requests
import pandas as pd
from io import StringIO

BASE_URL = st.secrets["api"]["BASE_URL"].rstrip('/')
API_TOKEN = st.secrets["api"]["API_TOKEN"]

with open("options.json") as f:
    options = json.load(f)

st.title("Data Merger and Downloader")

folder_options = ["All"] + options.get("folders", [])
selected_folder = st.selectbox("Select Data Source:", folder_options)

st.sidebar.header("Filters")
flujos_filter = st.sidebar.multiselect("Select Flujo:", options["flujo"], default=options["flujo"][0])
años_filter = st.sidebar.multiselect("Select Año:", options["año"], default=options["año"][-1])
paises_filter = st.sidebar.multiselect("Select País:", options["pais_nombre"], default=options["pais_nombre"][0])

def load_and_filter_data(folder, file_url):
    """Load data and apply filters only for existing columns"""
    response = requests.get(
        file_url,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        df['source_folder'] = folder
        
        # Apply filters only for columns that exist
        mask = pd.Series(True, index=df.index)
        if "flujo" in df.columns:
            mask &= df["flujo"].isin(flujos_filter)
        if "año" in df.columns:
            mask &= df["año"].isin(años_filter)
        if "pais_nombre" in df.columns:
            mask &= df["pais_nombre"].isin(paises_filter)
            
        return df[mask]
    return None

if st.sidebar.button("Apply Filters"):
    folders_to_process = options["folders"] if selected_folder == "All" else [selected_folder]
    all_dataframes = []
    
    # First load all dataframes
    for folder in folders_to_process:
        try:
            url = f"{BASE_URL}/data/{folder}/files"
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {API_TOKEN}"}
            )
            
            if response.status_code == 200 and "files" in response.json():
                files = response.json()["files"]
                
                for file in files:
                    file_url = f"{BASE_URL}/data/{folder}/{file}"
                    df = load_and_filter_data(folder, file_url)
                    if df is not None and not df.empty:
                        all_dataframes.append({
                            'data': df,
                            'source': folder,
                            'file': file
                        })
                        
        except Exception as e:
            st.error(f"Error processing folder {folder}: {str(e)}")

    if all_dataframes:
        st.write("### Processing Datasets")
        
        # Find common columns between all dataframes
        common_columns = set.intersection(*[set(df['data'].columns) for df in all_dataframes])
        st.write(f"Common columns found: {', '.join(common_columns)}")
        
        # Merge all dataframes
        final_df = all_dataframes[0]['data']
        
        for i in range(1, len(all_dataframes)):
            # Merge based on common columns, keeping all rows from both dataframes
            final_df = pd.merge(
                final_df,
                all_dataframes[i]['data'],
                on=list(common_columns),
                how='outer',
                suffixes=(f'_{all_dataframes[0]["source"]}', f'_{all_dataframes[i]["source"]}')
            )
        
        # Sort by common columns if they exist
        sort_columns = [col for col in ['año', 'pais_nombre'] if col in common_columns]
        if sort_columns:
            final_df = final_df.sort_values(sort_columns)
        
        st.write(f"### Final Merged Dataset")
        st.write(f"Total rows: {len(final_df)}")
        st.write(f"Total columns: {len(final_df.columns)}")
        
        # Display sources used
        sources = [df['source'] for df in all_dataframes]
        st.write(f"Sources merged: {', '.join(sources)}")
        
        # Show sample of the data
        st.dataframe(final_df)
        
        # Download button for final dataset
        csv_data = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Merged Dataset",
            csv_data,
            "merged_data.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.warning("No data found matching the selected filters.")
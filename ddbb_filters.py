#functions to work with database


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
        df['source_database'] = folder
        
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
    
    # Debug information
    st.write("### Loading Data")
    
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
                folder_data = []
                
                for file in files:
                    file_url = f"{BASE_URL}/data/{folder}/{file}"
                    df = load_and_filter_data(folder, file_url)
                    if df is not None and not df.empty:
                        folder_data.append(df)
                
                if folder_data:
                    # Combine all files from this folder
                    combined_df = pd.concat(folder_data, ignore_index=True)
                    st.write(f"Loaded {folder}: {len(combined_df)} rows, {len(combined_df.columns)} columns")
                    all_dataframes.append({
                        'data': combined_df,
                        'source': folder
                    })
                        
        except Exception as e:
            st.error(f"Error processing folder {folder}: {str(e)}")

    if len(all_dataframes) > 0:
        # If we're processing a single database
        if len(all_dataframes) == 1:
            final_df = all_dataframes[0]['data']
        # If we're merging multiple databases
        else:
            # Find common columns
            common_columns = set.intersection(*[set(df['data'].columns) - {'source_database'} 
                                             for df in all_dataframes])
            st.write(f"Common columns found: {', '.join(common_columns)}")
            
            # Start with the first dataframe
            final_df = all_dataframes[0]['data']
            st.write(f"Starting with {all_dataframes[0]['source']}: {len(final_df)} rows")
            
            # Merge with subsequent dataframes
            for i in range(1, len(all_dataframes)):
                current_df = all_dataframes[i]['data']
                st.write(f"Merging with {all_dataframes[i]['source']}: {len(current_df)} rows")
                
                # Rename non-common columns before merge
                for col in final_df.columns:
                    if col not in common_columns and col != 'source_database':
                        final_df = final_df.rename(columns={col: f"{col}_{all_dataframes[0]['source']}"})
                
                for col in current_df.columns:
                    if col not in common_columns and col != 'source_database':
                        current_df = current_df.rename(columns={col: f"{col}_{all_dataframes[i]['source']}"})
                
                # Merge on common columns
                final_df = pd.merge(
                    final_df,
                    current_df,
                    on=list(common_columns),
                    how='outer'
                )
                st.write(f"After merge: {len(final_df)} rows")
        
        # Sort by common columns if they exist
        sort_columns = [col for col in ['año', 'pais_nombre'] if col in final_df.columns]
        if sort_columns:
            final_df = final_df.sort_values(sort_columns)
        
        st.write(f"### Final Dataset")
        st.write(f"Total rows: {len(final_df)}")
        st.write(f"Total columns: {len(final_df.columns)}")
        
        # Show column names
        st.write("### Columns in final dataset:")
        st.write(", ".join(final_df.columns))
        
        # Show the data
        st.dataframe(final_df)
        
        # Download button for final dataset
        csv_data = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Dataset",
            csv_data,
            "merged_data.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.warning("No data found matching the selected filters.")





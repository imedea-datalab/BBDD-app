import streamlit as st
import os
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:5000/data"
API_TOKEN = "your_secret_token"

def fetch_csv_from_api(year):
    # Your existing fetch_csv_from_api function
    file_name = f"comex_taric_{year}.csv"
    url = f"{BASE_URL}/{file_name}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        local_file = f"/tmp/{file_name}"
        with open(local_file, "wb") as f:
            f.write(response.content)
        return pd.read_csv(local_file)
    else:
        st.error(f"Failed to fetch {file_name}: {response.status_code}")
        return pd.DataFrame()

def load_data():
    data = [fetch_csv_from_api(year) for year in range(1995, 2024)]
    return pd.concat(data)

def apply_filters(data, flujo_filter, año_filter, pais_filter, provincia_filter):
    return data[
        (data["flujo"].isin(flujo_filter))
        & (data["año"].isin(año_filter))
        & (data["pais_nombre"].isin(pais_filter))
        & (data["provincia_nombre"].isin(provincia_filter))
    ]

# Streamlit App
st.title("Data Filter and Merger")

# Create two columns for filtering different datasets
col1, col2 = st.columns(2)

# Load the base data once
base_data = load_data()

# First dataset filters
with col1:
    st.header("Dataset 1 Filters")
    
    flujo_filter1 = st.multiselect(
        "Select Flujo (1):", 
        options=base_data["flujo"].unique(), 
        default=base_data["flujo"].unique(),
        key="flujo1"
    )
    año_filter1 = st.multiselect(
        "Select Año (1):", 
        options=base_data["año"].unique(), 
        default=base_data["año"].unique()[-1],
        key="año1"
    )
    pais_filter1 = st.multiselect(
        "Select País (1):",
        options=base_data["pais_nombre"].unique(),
        default=base_data["pais_nombre"].unique()[0],
        key="pais1"
    )
    provincia_filter1 = st.multiselect(
        "Select Provincia (1):",
        options=base_data["provincia_nombre"].unique(),
        default=base_data["provincia_nombre"].unique(),
        key="provincia1"
    )
    
    # Apply filters to first dataset
    filtered_data1 = apply_filters(
        base_data, 
        flujo_filter1, 
        año_filter1, 
        pais_filter1, 
        provincia_filter1
    )
    
    st.write(f"Dataset 1 rows: {len(filtered_data1)}")
    st.dataframe(filtered_data1)

# Second dataset filters
with col2:
    st.header("Dataset 2 Filters")
    
    flujo_filter2 = st.multiselect(
        "Select Flujo (2):", 
        options=base_data["flujo"].unique(), 
        default=base_data["flujo"].unique(),
        key="flujo2"
    )
    año_filter2 = st.multiselect(
        "Select Año (2):", 
        options=base_data["año"].unique(), 
        default=base_data["año"].unique()[-1],
        key="año2"
    )
    pais_filter2 = st.multiselect(
        "Select País (2):",
        options=base_data["pais_nombre"].unique(),
        default=base_data["pais_nombre"].unique()[0],
        key="pais2"
    )
    provincia_filter2 = st.multiselect(
        "Select Provincia (2):",
        options=base_data["provincia_nombre"].unique(),
        default=base_data["provincia_nombre"].unique(),
        key="provincia2"
    )
    
    # Apply filters to second dataset
    filtered_data2 = apply_filters(
        base_data, 
        flujo_filter2, 
        año_filter2, 
        pais_filter2, 
        provincia_filter2
    )
    
    st.write(f"Dataset 2 rows: {len(filtered_data2)}")
    st.dataframe(filtered_data2)

# Merge section
st.header("Merge Datasets")
merge_type = st.radio(
    "Select merge type:",
    ("Concatenate (Stack)", "Union (Unique rows)", "Intersection (Common rows)")
)

if st.button("Merge Datasets"):
    if merge_type == "Concatenate (Stack)":
        merged_data = pd.concat([filtered_data1, filtered_data2], axis=0, ignore_index=True)
    elif merge_type == "Union (Unique rows)":
        merged_data = pd.concat([filtered_data1, filtered_data2], axis=0).drop_duplicates().reset_index(drop=True)
    else:  # Intersection
        merged_data = pd.merge(filtered_data1, filtered_data2, how='inner')
    
    st.subheader("Merged Data Preview")
    st.write(f"Total rows after merging: {len(merged_data)}")
    st.dataframe(merged_data)
    
    # Download button for merged data
    csv_data = merged_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Merged Data",
        data=csv_data,
        file_name="merged_filtered_data.csv",
        mime="text/csv",
    )
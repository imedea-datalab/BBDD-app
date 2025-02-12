import streamlit as st
import os
import requests
import pandas as pd
import numpy as np


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

def calculate_additional_metrics(df1, df2):
    """
    Calculate additional metrics from the two dataframes
    Returns a new dataframe with the calculated results
    """
    # Create a new dataframe with the calculations
    results_df = pd.DataFrame()
    
    # Example calculations - modify these based on your needs
    # Assuming you have 'value' columns in both dataframes
    results_df['total_value'] = df1['value'].values + df2['value'].values
    
    # You can add more calculations as needed
    results_df['average_value'] = (df1['value'].values + df2['value'].values) / 2
    results_df['difference'] = df1['value'].values - df2['value'].values
    
    # Copy relevant columns from original dataframes if needed
    results_df['año'] = df1['año']  # Assuming 'año' is a relevant column to keep
    results_df['pais_nombre'] = df1['pais_nombre']
    
    return results_df


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

# In your main app section:
if st.button("Merge Datasets and Calculate"):
    if merge_type == "Concatenate (Stack)":
        merged_data = pd.concat([filtered_data1, filtered_data2], axis=0, ignore_index=True)
    elif merge_type == "Union (Unique rows)":
        merged_data = pd.concat([filtered_data1, filtered_data2], axis=0).drop_duplicates().reset_index(drop=True)
    else:  # Intersection
        merged_data = pd.merge(filtered_data1, filtered_data2, how='inner')
    
    # Calculate additional metrics
    st.subheader("Calculations Results")
    
    # First, ensure the dataframes are aligned properly
    # You might need to merge on specific columns
    calc_ready_df1 = filtered_data1.sort_values(['año', 'pais_nombre']).reset_index(drop=True)
    calc_ready_df2 = filtered_data2.sort_values(['año', 'pais_nombre']).reset_index(drop=True)
    
    if len(calc_ready_df1) == len(calc_ready_df2):
        calculations_df = calculate_additional_metrics(calc_ready_df1, calc_ready_df2)
        st.write("Calculated Metrics:")
        st.dataframe(calculations_df)
        
        # Add download button for calculations
        calc_csv = calculations_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Calculations CSV",
            data=calc_csv,
            file_name="calculations_results.csv",
            mime="text/csv",
        )
    else:
        st.warning("Unable to perform calculations: Datasets have different numbers of rows. Please ensure filters result in matching datasets.")
    
    # Original merged data preview
    st.subheader("Merged Data Preview")
    st.write(f"Total rows after merging: {len(merged_data)}")
    st.dataframe(merged_data)
    
    # Download button for merged data
    merged_csv = merged_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Merged Data",
        data=merged_csv,
        file_name="merged_filtered_data.csv",
        mime="text/csv",
    )
# Add this before the merge button
st.subheader("Select Calculations")
calculations = st.multiselect(
    "Choose calculations to perform:",
    [
        "Sum of values",
        "Average values",
        "Percentage difference",
        "Growth rate",
        "Custom calculation"
    ]
)

# If custom calculation is selected, show input for formula
if "Custom calculation" in calculations:
    custom_formula = st.text_input(
        "Enter custom calculation formula (use 'df1' and 'df2' as dataframe names)",
        "df1['value'] * df2['value']"
    )

# Modify the calculate_additional_metrics function to use selected calculations
def calculate_additional_metrics(df1, df2, selected_calcs, custom_formula=None):
    results_df = pd.DataFrame()
    
    for calc in selected_calcs:
        if calc == "Sum of values":
            results_df['sum_values'] = df1['value'] + df2['value']
        elif calc == "Average values":
            results_df['avg_values'] = (df1['value'] + df2['value']) / 2
        elif calc == "Percentage difference":
            results_df['pct_diff'] = ((df2['value'] - df1['value']) / df1['value']) * 100
        elif calc == "Growth rate":
            results_df['growth_rate'] = (df2['value'] / df1['value']) - 1
        elif calc == "Custom calculation" and custom_formula:
            try:
                results_df['custom_calc'] = eval(custom_formula)
            except Exception as e:
                st.error(f"Error in custom calculation: {str(e)}")
    
    # Copy relevant columns
    results_df['año'] = df1['año']
    results_df['pais_nombre'] = df1['pais_nombre']
    
    return results_df
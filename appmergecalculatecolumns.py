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

def merge_and_calculate(df1, df2, selected_columns):
    """
    Merge dataframes and add calculation columns based on selected headers
    """
    # First merge the dataframes on common identifying columns
    # Adjust these columns based on your data structure
    merge_on = ['año', 'pais_nombre', 'provincia_nombre']
    
    # Add suffixes to distinguish columns from different datasets
    merged_df = pd.merge(df1, df2, on=merge_on, suffixes=('_df1', '_df2'))
    
    # Add calculation columns for selected headers
    for col in selected_columns:
        col_df1 = f"{col}_df1"
        col_df2 = f"{col}_df2"
        
        if col_df1 in merged_df.columns and col_df2 in merged_df.columns:
            # Add sum column
            merged_df[f"{col}_sum"] = merged_df[col_df1] + merged_df[col_df2]
            # Add difference column
            merged_df[f"{col}_diff"] = merged_df[col_df1] - merged_df[col_df2]
            # Add percentage change column
            merged_df[f"{col}_pct_change"] = ((merged_df[col_df2] - merged_df[col_df1]) / 
                                            merged_df[col_df1] * 100).round(2)
    
    return merged_df

# In your main app section:
st.title("Data Filter and Merger with Calculations")

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

## Merge section
#st.header("Merge Datasets")
#merge_type = st.radio(
#    "Select merge type:",
#    ("Concatenate (Stack)", "Union (Unique rows)", "Intersection (Common rows)")
#)
# Add column selection for calculations
st.header("Select Columns for Calculations")
common_columns = list(set(filtered_data1.columns) & set(filtered_data2.columns))
numeric_columns = [col for col in common_columns 
                  if pd.api.types.is_numeric_dtype(filtered_data1[col])]

selected_columns = st.multiselect(
    "Select columns to calculate:",
    options=numeric_columns,
    help="Select the columns you want to perform calculations on"
)



if st.button("Merge and Calculate"):
    try:
        # Merge and calculate
        result_df = merge_and_calculate(filtered_data1, filtered_data2, selected_columns)
        
        # Show results
        st.subheader("Results")
        st.write(f"Total rows: {len(result_df)}")
        
        # Display column descriptions
        st.write("Column descriptions:")
        for col in selected_columns:
            st.write(f"- {col}_sum: Sum of values from both datasets")
            st.write(f"- {col}_diff: Difference between datasets (Dataset 2 - Dataset 1)")
            st.write(f"- {col}_pct_change: Percentage change between datasets")
        
        # Show the dataframe
        st.dataframe(result_df)
        
        # Download button
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="calculated_results.csv",
            mime="text/csv"
        )
        
        # Show summary statistics
        st.subheader("Summary Statistics")
        for col in selected_columns:
            st.write(f"\nStatistics for {col}:")
            stats_df = pd.DataFrame({
                'Sum': [result_df[f"{col}_sum"].mean()],
                'Average Difference': [result_df[f"{col}_diff"].mean()],
                'Average % Change': [result_df[f"{col}_pct_change"].mean()]
            }).round(2)
            st.dataframe(stats_df)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check if:")
        st.write("- The selected columns exist in both datasets")
        st.write("- The columns contain numeric values")
        st.write("- The datasets have matching rows for merging")
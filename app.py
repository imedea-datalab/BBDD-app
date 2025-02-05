import streamlit as st
import os
import pandas as pd

# Read the data path from secrets.toml
DATA_PATH = st.secrets["paths"]["DATA_PATH"]


# Load the dataset
def load_data():
    data = []
    for year in range(1995, 2024):
        file_path = os.path.join(
            DATA_PATH, f"DataComex_output_with_metadata/comex_taric_{year}.csv"
        )
        data.append(pd.read_csv(file_path))
    return pd.concat(data)


data = load_data()

# Streamlit App
st.title("Filtered Data Downloader")
st.markdown("Use the filters below to refine the data and download it as a CSV file.")

# Filters
st.sidebar.header("Filters")
flujo_filter = st.sidebar.multiselect(
    "Select Flujo:", options=data["flujo"].unique(), default=data["flujo"].unique()
)
año_filter = st.sidebar.multiselect(
    "Select Año:", options=data["año"].unique(), default=data["año"].unique()[-1]
)
pais_filter = st.sidebar.multiselect(
    "Select País:",
    options=data["pais_nombre"].unique(),
    default=data["pais_nombre"].unique()[0],
)
provincia_filter = st.sidebar.multiselect(
    "Select Provincia:",
    options=data["provincia_nombre"].unique(),
    default=data["provincia_nombre"].unique(),
)

# Apply filters
filtered_data = data[
    (data["flujo"].isin(flujo_filter))
    & (data["año"].isin(año_filter))
    & (data["pais_nombre"].isin(pais_filter))
    & (data["provincia_nombre"].isin(provincia_filter))
]

# Data preview
st.subheader("Filtered Data Preview")
st.write(f"Displaying {len(filtered_data)} rows of data")
st.dataframe(filtered_data)

# Download button
st.subheader("Download Filtered Data")


def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")


csv_data = convert_df_to_csv(filtered_data)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="filtered_data.csv",
    mime="text/csv",
)

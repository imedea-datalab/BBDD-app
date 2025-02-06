import streamlit as st
import os
import requests
import pandas as pd

# Read the data path from secrets.toml
# Accessing secrets
# BASE_URL = st.secrets["api"]["BASE_URL"]
# API_TOKEN = st.secrets["api"]["API_TOKEN"]

# Read API details from Streamlit secrets
# BASE_URL = os.environ.get("BASE_URL")
# API_TOKEN = os.environ.get("API_TOKEN")

BASE_URL = "http://127.0.0.1:5000/data"
API_TOKEN = "your_secret_token"


# Fetch CSV from the API and return as DataFrame
def fetch_csv_from_api(year):
    file_name = f"comex_taric_{year}.csv"
    url = f"{BASE_URL}/{file_name}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # Fetch the CSV file
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        local_file = f"/tmp/{file_name}"
        with open(local_file, "wb") as f:
            f.write(response.content)
        return pd.read_csv(local_file)
    else:
        st.error(f"Failed to fetch {file_name}: {response.status_code}")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure


# Load data from multiple years
def load_data():
    data = [fetch_csv_from_api(year) for year in range(1995, 2024)]
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

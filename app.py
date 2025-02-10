import streamlit as st
import os
import json
import requests
import pandas as pd

# Read the data path from secrets.toml
# Accessing secrets
# BASE_URL = st.secrets["api"]["BASE_URL"]
# API_TOKEN = st.secrets["api"]["API_TOKEN"]

# Read API details from Streamlit secrets
# BASE_URL = os.environ.get("BASE_URL")
# API_TOKEN = os.environ.get("API_TOKEN")

BASE_URL = st.secrets["api"]["BASE_URL"]
API_TOKEN = st.secrets["api"]["API_TOKEN"]


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


# Read options.json
with open("options.json") as f:
    options = json.load(f)


# Load data from multiple years
def load_data(años_filter=None):
    data = []
    for año in años_filter:
        data.append(fetch_csv_from_api(año))

    return pd.concat(data)


# Streamlit App
st.title("Filtered Data Downloader")
st.markdown("Use the filters below to refine the data and download it as a CSV file.")


# Filters
st.sidebar.header("Filters")
flujos_filter = st.sidebar.multiselect(
    "Select Flujo:",
    options=options["flujo"],
    default=options["flujo"][0],
)
años_filter = st.sidebar.multiselect(
    "Select Año:", options=options["año"], default=options["año"][-1]
)
paises_filter = st.sidebar.multiselect(
    "Select País:",
    options=options["pais_nombre"],
    default=options["pais_nombre"][0],
)


# Data preview
st.subheader("Filtered Data Preview")
# st.write(f"Displaying {len(data)} rows of data")

# Put a button to apply the filters
if st.sidebar.button("Apply Filters"):
    data = load_data(años_filter)
    # Apply filters
    filtered_data = data[
        (data["flujo"].isin(flujos_filter)) & (data["pais_nombre"].isin(paises_filter))
    ]
    st.write(f"Displaying {len(filtered_data)} rows of data")
    st.dataframe(filtered_data)
    st.sidebar.success("Filters Applied!")

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

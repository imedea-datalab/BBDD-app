import streamlit as st
import pandas as pd
import json

import streamlit_app.data_processing as data_processing

# Read options from options.json (this file should include your filter options)
with open("options.json") as f:
    options = json.load(f)

# Streamlit App Title and Description
st.title("Filtered Data Downloader")
st.markdown("Use the filters below to refine the data and download it as a CSV file.")

# Sidebar Filters
st.sidebar.header("Filters")

# New database selection widget
selected_database = st.sidebar.selectbox(
    "Select Data database", options=options["database"], index=0
)

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
    options=sorted(options["pais_nombre"]),
    default=options["pais_nombre"][0],
)

# Data Preview Section
st.subheader("Filtered Data Preview")

# When the user clicks the button, load the data and apply the filters
if st.sidebar.button("Apply Filters"):
    data_frames = []
    for año in años_filter:
        df = data_processing.fetch_csv_from_api(selected_database, año)
        data_frames.append(df)

    # Concatenate data from all selected years.
    if data_frames:
        data = pd.concat(data_frames)
    else:
        data = pd.DataFrame()

    # Apply additional filters to the combined DataFrame.
    filtered_data = data[
        (data["flujo"].isin(flujos_filter)) & (data["pais_nombre"].isin(paises_filter))
    ]

    st.write(f"Displaying {len(filtered_data)} rows of data")
    st.dataframe(filtered_data)
    st.sidebar.success("Filters Applied!")

    # Download Button Section
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

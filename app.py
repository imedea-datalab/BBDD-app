import streamlit as st
import pandas as pd
import json

# Supongamos que aquí tienes tu cliente que se encarga de descargar y procesar los CSV
from client.data_processing import fetch_csv_from_api

# 1. Cargar opciones
with open("options.json") as f:
    options = json.load(f)

# 2. Título y descripción
st.title("Aplicación de Datos con Múltiples Bases")
st.markdown(
    "Puedes añadir varias bases de datos y aplicar filtros distintos a cada una."
)
# 3. Manejo de session_state para almacenar la configuración de cada base de datos
if "database_entries" not in st.session_state:
    # Cada elemento de esta lista representará un conjunto de filtros para una base de datos
    st.session_state["database_entries"] = []
    st.session_state["database_entries"].append(
        {
            "id": len(st.session_state["database_entries"]),  # identificador interno
            "database": None,
            "flujos_filter": [],
            "años_filter": [],
            "paises_filter": [],
        }
    )


# Función que se llama al pulsar el botón "Añadir base de datos"
def add_database():
    """
    Añade un nuevo conjunto de filtros (vacío) a la lista 'database_entries'.
    """
    st.session_state["database_entries"].append(
        {
            "id": len(st.session_state["database_entries"]),  # identificador interno
            "database": None,
            "flujos_filter": [],
            "años_filter": [],
            "paises_filter": [],
        }
    )


# 4. Renderizar dinámicamente cada bloque de filtros
used_databases = [
    entry["database"]
    for entry in st.session_state["database_entries"]
    if entry["database"]
]

for entry in st.session_state["database_entries"]:
    st.sidebar.subheader(f"Configuración para base de datos #{entry['id']+1}")

    # Filtrar opciones de base de datos para excluir las ya seleccionadas
    available_databases = [
        db
        for db in options["database"]
        if db not in used_databases or db == entry["database"]
    ]

    # Seleccionar base de datos
    entry["database"] = st.sidebar.selectbox(
        "Selecciona la base de datos",
        options=available_databases,
        key=f"database_{entry['id']}",  # clave única para que Streamlit recuerde la selección
    )

    # Filtro de flujo
    selected_flujos = st.sidebar.multiselect(
        "Selecciona Flujo",
        options=options["flujo"],
        default=options["flujo"][0],
        key=f"flujo_{entry['id']}",
    )
    entry["flujos_filter"] = selected_flujos

    # Filtro de año
    all_anos = ["Seleccionar todos"] + options["año"]
    selected_anos = st.sidebar.multiselect(
        "Selecciona Año",
        options=all_anos,
        default=all_anos[-1],
        key=f"ano_{entry['id']}",
    )
    if "Seleccionar todos" in selected_anos:
        entry["años_filter"] = options["año"]
    else:
        entry["años_filter"] = selected_anos

    # Filtro de país
    all_paises = ["Seleccionar todos"] + options["pais"]
    selected_paises = st.sidebar.multiselect(
        "Selecciona País",
        options=all_paises,
        default=all_paises[1],
        key=f"pais_{entry['id']}",
    )
    if "Seleccionar todos" in selected_paises:
        entry["paises_filter"] = options["pais"]
    else:
        entry["paises_filter"] = selected_paises

    st.sidebar.write("---")

# Botón para añadir un nuevo bloque de filtros
if len(st.session_state["database_entries"]) < len(options["database"]):
    st.sidebar.button("Añadir base de datos", on_click=add_database)
else:
    st.sidebar.write("No hay más bases de datos disponibles para añadir.")

# 5. Botón para aplicar filtros a todas las bases de datos añadidas
if st.sidebar.button("Aplicar filtros a todas las BBDD"):
    progress_bar = st.progress(0)

    # Calcular todos los años seleccionados de las BBDD
    all_selected_years = []
    for entry in st.session_state["database_entries"]:
        all_selected_years.extend(entry["años_filter"])
    print(len(all_selected_years))
    y = 0

    # st.write(f"Años seleccionados: {sorted(all_selected_years)}")

    with st.spinner("Procesando datos..."):
        all_dataframes = []

        # Recorrer cada configuración de base de datos
        for idx, entry in enumerate(st.session_state["database_entries"]):
            db_name = entry["database"]
            flujos = entry["flujos_filter"]
            years = entry["años_filter"]
            paises = entry["paises_filter"]

            # Cargar los datos para cada año
            data_frames = []
            for year in years:
                df = fetch_csv_from_api(db_name, year)
                data_frames.append(df)
                # Actualizar barra de progreso
                progress_bar.progress((y + 1) / len(all_selected_years))
                y += 1

            if data_frames:
                combined_df = pd.concat(data_frames)
            else:
                combined_df = pd.DataFrame()

            # Aplicar los filtros
            filtered_df = combined_df[
                (combined_df["flujo"].isin(flujos)) & (combined_df["pais"].isin(paises))
            ]

            # Guardar resultado de esta base de datos
            all_dataframes.append(filtered_df)

        ########################################################
        # Aquí faltaría implementar el merge de los dataframes #
        ########################################################

        # Crear pestañas para cada base de datos filtrada
        tabs = st.tabs(
            [f"Base de datos #{idx + 1}" for idx in range(len(all_dataframes))]
        )

        for idx, (tab, df) in enumerate(zip(tabs, all_dataframes)):
            with tab:
                st.subheader(f"Resultado para base de datos #{idx + 1}")
                st.write(f"Mostrando {len(df)} filas de datos")
                st.dataframe(df, use_container_width=True)

                # Opción de descarga
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Descargar CSV combinado",
                    data=csv_data,
                    file_name=f"filtered_data_{idx + 1}.csv",
                    mime="text/csv",
                )

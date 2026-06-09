import streamlit as st
import sqlite3
import pandas as pd
import time

RUTA_DB = "/srv/reportes_staxx/db/tracking.db"
TITULO = "Monitor de Facturas"

def cargar_datos():
    try:
        conn = sqlite3.connect(RUTA_DB)
        query = "SELECT archivo AS Archivo, estado AS Estado, fecha AS 'Última Actualización' FROM facturas ORDER BY fecha DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def main():
    st.set_page_config(page_title=TITULO, page_icon="📄", layout="wide")
    st.title("Monitor en Vivo: Procesamiento de IA")

    placeholder = st.empty()

    while True:
        df = cargar_datos()
        with placeholder.container():
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay facturas registradas en el sistema todavía.")
                
        time.sleep(3)

if __name__ == "__main__":
    main()
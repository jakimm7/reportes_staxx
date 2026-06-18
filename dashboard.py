import streamlit as st
from interface.interface import init, subir_facturas, subir_resumen

RUTA_DB = "/srv/reportes_staxx/db/tracking.db"
TITULO = "Staxx Reporter"
BOTON_SUBIR = "📂 Subir reportes"
BOTON_TRANSCRIBIR = "📊 Transcribir al Excel"
ESTADO_CARGADO_EN_DB = "✅ Cargado en DB"
ESTADO_ERROR_CARGA_DB = "❌ Error de Escritura"

def main():
    st.set_page_config(page_title="Staxx Reportes", page_icon="📄", layout="centered")
    st.title("📄 Procesador de Facturas")
    st.divider()

    client, ruta_reportes, ruta_resumen, ruta_procesados = init()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(BOTON_SUBIR, use_container_width=True):
            with st.spinner("Procesando facturas..."):
                resultados = subir_facturas(client, ruta_reportes, ruta_procesados)

            if isinstance(resultados, str):
                st.warning(resultados)
            else:
                for tipo, mensaje in resultados:
                    if tipo == "ok":
                        st.success(mensaje)
                    else:
                        st.error(mensaje)

    with col2:
        if st.button("📊 Transcribir a Excel", use_container_width=True):
            with st.spinner("Transcribiendo..."):
                resultado = subir_resumen(ruta_resumen)

            if isinstance(resultado, str):
                st.warning(resultado)
            else:
                tipo, mensaje = resultado
                if tipo == "ok":
                    st.success(mensaje)
                else:
                    st.error(mensaje)

if __name__ == "__main__":
    main()
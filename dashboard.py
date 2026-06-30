import streamlit as st
from interface.interface import init, accion_subir, accion_resumen

ICONO_PAGINA = "📄"
TITULO = f"{ICONO_PAGINA} Procesador de Reportes de Ventas"
TITULO_PAGINA = "Staxx Reporter"
BOTON_SUBIR = "📂 Subir reportes"
BOTON_TRANSCRIBIR = "📊 Transcribir al Excel"
TEXTO_PROCESANDO = "Procesando facturas..."
TEXTO_TRANSCRIBIENDO = "Transcribiendo..."

ALINEACION_PAGINA = "centered"

def main():
    st.set_page_config(page_title=TITULO_PAGINA, page_icon=ICONO_PAGINA, layout=ALINEACION_PAGINA)
    st.title(TITULO)
    st.divider()

    client, ruta_reportes, ruta_resumen, ruta_procesados = init()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(BOTON_SUBIR, use_container_width=True):
            with st.spinner(TEXTO_PROCESANDO):
                resultados = accion_subir(client, ruta_reportes, ruta_procesados)

            if isinstance(resultados, str):
                st.warning(resultados)
            else:
                for tipo, mensaje in resultados:
                    if tipo == "ok":
                        st.success(mensaje)
                    else:
                        st.error(mensaje)

    with col2:
        if st.button(BOTON_TRANSCRIBIR, use_container_width=True):
            with st.spinner(TEXTO_TRANSCRIBIENDO):
                resultado = accion_resumen(ruta_resumen)

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
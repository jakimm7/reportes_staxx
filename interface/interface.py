from parse_ai.parse_ai import parsear_data_reporte, init_ai_api
from proceso.proceso import procesar_data, transcribir_excel
from utils.utils import cargar_tipo_cambio, init_paths, mover_archivo
from db.db import obtener_ventas_nuevas, marcar_venta_cargada, cargar_venta, init_sales_db

NUMERO_OP = 5
NUMERO_FC = 6
ERROR_EXCEL_ABIERTO = "El archivo Excel está abierto. Cerralo e intentá de nuevo."

def init():
    ruta_env, ruta_reportes, ruta_resumen, ruta_procesados = init_paths()
    client = init_ai_api(ruta_env)
    init_sales_db()
    return client, ruta_reportes, ruta_resumen, ruta_procesados

def subir_facturas(client, ruta_reportes, ruta_procesados):
    archivos_nuevos = [f for f in ruta_reportes.iterdir() if f.is_file() and not f.name.startswith('.')]

    if not archivos_nuevos:
        return "No hay reportes nuevos en la carpeta."

    tipo_cambio = cargar_tipo_cambio()
    if not tipo_cambio:
        return "No se pudo obtener el tipo de cambio. Intentá de nuevo."
    _, tc_venta = tipo_cambio

    resultados = []
    for ruta_archivo in archivos_nuevos:
        datos_venta = parsear_data_reporte(ruta_archivo, client)
        if datos_venta is None:
            resultados.append(("error", f"Error de lectura en: {ruta_archivo.name}"))
            continue

        datos_venta = procesar_data(datos_venta, tc_venta)

        try:
            cargar_venta(datos_venta)
            mover_archivo(ruta_archivo, ruta_procesados)
            resultados.append(("ok", f"{ruta_archivo.name} cargado correctamente."))
        except Exception as e:
            resultados.append(("error", f"Error al cargar {ruta_archivo.name}: {e}"))

    return resultados

def subir_resumen(ruta_resumen):
    ventas = obtener_ventas_nuevas()

    if not ventas:
        return "No hay ventas pendientes de transcribir."

    try:
        for datos_venta in ventas:
            transcribir_excel(datos_venta, ruta_resumen)
            marcar_venta_cargada(datos_venta[NUMERO_OP], datos_venta[NUMERO_FC])
        return ("ok", f"{len(ventas)} venta(s) transcripta(s) correctamente.")
    except PermissionError:
        return ("error", ERROR_EXCEL_ABIERTO)
    except Exception as e:
        return ("error", f"Error al transcribir: {e}")
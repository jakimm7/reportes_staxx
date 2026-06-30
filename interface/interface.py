from parse_ai.parse_ai import parsear_data_reporte, init_ai_api
from proceso.proceso import procesar_data, transcribir_excel
from utils.utils import cargar_tipo_cambio, init_paths, mover_archivo, archivo_elegible
from db.db import obtener_ventas_nuevas, marcar_venta_cargada, cargar_venta, init_sales_db

NUMERO_OP = 5
NUMERO_FC = 6
ERROR_EXCEL_ABIERTO = "El archivo Excel está abierto. Cerralo e intentá de nuevo."

TC_VENTA = 1

def init():
    ruta_env, ruta_reportes, ruta_resumen, ruta_procesados = init_paths()
    client = init_ai_api(ruta_env)
    init_sales_db()
    return client, ruta_reportes, ruta_resumen, ruta_procesados

def accion_subir(client, ruta_reportes, ruta_procesados):
    archivos_nuevos = [archivo for archivo in ruta_reportes.iterdir() if archivo_elegible(archivo)]
    if not archivos_nuevos:
        return "No hay reportes nuevos en la carpeta."

    tipo_cambio = cargar_tipo_cambio()
    if not tipo_cambio:
        return "No se pudo obtener el tipo de cambio. Intentá de nuevo."

    resultados = []
    for archivo in archivos_nuevos:
        resultados = procesar_factura(archivo, resultados, tipo_cambio[TC_VENTA], client)

    return resultados

def accion_resumen(ruta_resumen):
    ventas = obtener_ventas_nuevas()
    if not ventas:
        return "No hay ventas pendientes de transcribir."

    actualizar_resumen(ventas, ruta_resumen)
    
def actualizar_resumen(ventas, ruta_resumen):
    try:
        for datos_venta in ventas:
            transcribir_excel(ruta_resumen, datos_venta, "mayo", "VENTAS_MAYO")
            marcar_venta_cargada((datos_venta[NUMERO_OP], datos_venta[NUMERO_FC]))
        return ("ok", f"{len(ventas)} venta(s) transcripta(s) correctamente.")
    except PermissionError:
        return ("error", ERROR_EXCEL_ABIERTO)
    except Exception as e:
        return ("error", f"Error al transcribir: {e}")
    
def procesar_factura(archivo, procesados, tc, client):
    datos_venta = parsear_data_reporte(archivo, client)
    if datos_venta is None:
        procesados.append(("error", f"Error de lectura en: {archivo.name}"))
        return procesados

    datos_venta = procesar_data(datos_venta, tc)

    try:
        cargar_venta(datos_venta)
        mover_archivo(archivo, procesados)
        procesados.append(("ok", f"{archivo.name} cargado correctamente."))
    except Exception as e:
        procesados.append(("error", f"Error al cargar {archivo.name}: {e}"))
    
    return procesados
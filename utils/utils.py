import requests
from datetime import datetime
import shutil
from pathlib import Path
from copy import copy

RUTA_SAMBA = Path("/srv/reportes_staxx")
RUTA_APP = Path("/home/jakim/staxx_executive/staxx_reporter/env")

DOLAR_API_URL = "https://dolarapi.com/v1/dolares/oficial"
COMPRA = "compra"
VENTA = "venta"

FORMATO_FECHA = "%d/%m/%Y"

ARCHIVO_RESUMEN = "resumen"
EXTENSION_XLSX = ".xlsx"

def cargar_tipo_cambio():
    try:
        respuesta = requests.get(DOLAR_API_URL)
        datos_dolar = respuesta.json()
        return datos_dolar[COMPRA], datos_dolar[VENTA]
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return None
    
def init_paths():
    year = datetime.datetime.now().year
    nombre_archivo = f"{ARCHIVO_RESUMEN}_{year}{EXTENSION_XLSX}"
    ruta_env = RUTA_APP / "api-key.env"
    ruta_reportes = RUTA_SAMBA / "nuevos"
    ruta_procesados = RUTA_SAMBA / "procesados"
    ruta_resumen = RUTA_SAMBA / "resumenes" / nombre_archivo

    return ruta_env, ruta_reportes, ruta_resumen, ruta_procesados

def mover_archivo(archivo: Path, destino: Path):
    if archivo.exists() and destino.exists():
        ruta_destino_final = destino / archivo.name
        shutil.move(str(archivo), str(ruta_destino_final))    
    else:
        print("Error al mover el archivo: El directorio destino no existe")

def copiar_estilo(origen, destino):
    destino.number_format = origen.number_format
    destino.font = copy(origen.font)
    destino.fill = copy(origen.fill)
    destino.border = copy(origen.border)
    destino.alignment = copy(origen.alignment)

def procesar_fecha(fecha_cruda):
    return datetime.strptime(fecha_cruda, FORMATO_FECHA).strftime(FORMATO_FECHA)
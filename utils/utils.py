import requests
import datetime
import os
import shutil
from pathlib import Path

RUTA_SAMBA = Path("/srv/reportes_staxx")
RUTA_APP = Path("/home/jakim/staxx_executive/staxx_reporter")

DOLAR_API_URL = "https://dolarapi.com/v1/dolares/oficial"
COMPRA = "compra"
VENTA = "venta"

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
    month = datetime.datetime.now().month
    nombre_archivo = f"{ARCHIVO_RESUMEN}_{month}_{year}_{EXTENSION_XLSX}"
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
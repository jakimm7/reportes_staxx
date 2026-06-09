import time
from parse_ai.parse_ai import parsear_data_reporte, init_ai_api
from proceso.proceso import procesar_data, transcribir_excel
from utils.utils import cargar_tipo_cambio, init_paths, mover_archivo
from db.db import init_db, actualizar_estado

DIRECTORIO_REPORTES = "reportes"
DIRECTORIO_RESUMEN = "resumen"
DIRECTORIO_ENV = "env"
ARCHIVO_RESUMEN = "resumen"
ARCHIVO_ENV = "api-key.env"

def main():
    ruta_env, ruta_reportes, ruta_resumen, ruta_procesados = init_paths()
    client = init_ai_api(ruta_env)
    init_paths()
    
    if client is None:
        print(f"[CRÍTICO] No se encontró el motor de IA o API Key en: {ruta_env}")
        return
    
    print("Servidor iniciado correctamente. Esperando facturas en la carpeta 'nuevos'...")
    
    while True:
        try:
            archivos_nuevos = [f for f in ruta_reportes.iterdir() if f.is_file() and not f.name.startswith('.')]
            
            if archivos_nuevos:
                tipo_cambio = cargar_tipo_cambio()
                if tipo_cambio:
                    _, tc_venta = tipo_cambio
                else:
                    print("Esperando conexión a la API del dólar...")
                    time.sleep(15)
                    continue

                for ruta_archivo in archivos_nuevos:
                    print(f"\nProcesando: {ruta_archivo.name}")
                    actualizar_estado(ruta_archivo.name, "⏳ Procesando con IA")
                    datos_venta = parsear_data_reporte(ruta_archivo, client)
                    
                    if datos_venta is None:
                        print(f"[ERROR] Falló la IA para {ruta_archivo.name}. Se salteará este archivo.")
                        actualizar_estado(ruta_archivo.name, "❌ Error de Lectura")
                        continue
                    datos_venta = procesar_data(datos_venta, tc_venta)
                    
                    try:
                        transcribir_excel(datos_venta, ruta_resumen)
                        mover_archivo(ruta_archivo, ruta_procesados)
                        print(f"[ÉXITO] Archivo {ruta_archivo.name} procesado y movido.")
                        actualizar_estado(ruta_archivo.name, "✅ Completado")
                    except PermissionError:
                        print(f"[ADVERTENCIA] El Excel está abierto en alguna términal. Cerralo para que pueda guardar los datos de {ruta_archivo.name}")
                        actualizar_estado(ruta_archivo.name, "⚠️ Excel Bloqueado en Windows")
                    except Exception as e:
                        print(f"[ERROR] Falla al escribir Excel: {e}")
                        actualizar_estado(ruta_archivo.name, "❌ Error de Escritura")

            time.sleep(10)

        except Exception as e:
            print(f"Error general en el ciclo principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
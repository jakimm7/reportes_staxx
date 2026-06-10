import time
import json
import google.genai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

MODELO_AI = "gemini-2.5-flash"
REINTENTOS = 3
PROMPT =  """Analiza este documento de venta y extrae únicamente los siguientes datos en formato JSON estricto. 
                No apliques ninguna lógica adicional ni devuelvas campos que no se solicitan.

                1. "fecha": Pone la fecha en la cual se realizo la venta de ML o se facturo la venta, según corresponda. En formato DD/MM/AA
                2. "canal_venta": Si es una venta efectuada por Mercado Libre, pone "ML". Sino, pone "VENDEDOR"
                3. "entregado": Pone "NO" por defecto, sin importar si es por "ML" o "VENDEDOR"
                4. "cantidad": Completa con la cantidad de las estanterias que se vendieron en la operacion analizada.
                5. "producto": Si el producto vendido es una estanteria de 300 o 1200 KG, pone "300 KG". Caso contrario, pone "200 KG"
                6. "nombre_razon_social": Si es una venta de ML, distingui si la persona cuenta con CUIT. En ese caso, debes ingresar NOMBRE // RAZON SOCIAL. Caso contrario
                pone solo el nombre de la persona. Si es una Factura A, solo va la razon social.
                7. "numero_op": Si estas analizando una venta de ML, pone el numero de operación que te brinda el reporte. Si es una factura, deja el campo en blanco.
                8. "numero_fc": Si estas analizando una factura, pone el numero de ella. Caso contrario deja el campo en blanco.
                9. "direccion": Deja este campo completamente en blanco
                10. "horario": Al igual que en "direccion", no pongas ningun dato aqui.
                11. "dni_cuit": Si fuera el caso de una venta por "ML", pone el DNI o CUIT del cliente que figura en el reporte. Caso contrario, deja el campo vacío.
                12. "cobro_flete": Deja este campo completamente en blanco para los dos tipos de canales de venta.
                13. "medio_pago": Acá en caso de que sea una venta efectuada por "ML", completa este campo con "MP". Caso contrario, deja como dato "Transferencia"
                14. "comentarios": Esta campo debe estar completamente sin ningun tipo de dato
                15. "pago": Si es una venta efectuada por Mercado Libre, debes completar con un "SI". Caso contrario, completalo con un "NO"
                16. "valor_venta": Aca debes completar con el valor FINAL de la venta, sin contemplar IBB y cargos por venta en el caso de Mercado Libre. Para las ventas
                hechas por un canal de vendedor, tomar simplemente el valor final total contemplado en la factura o proforma.
                17. "cargo_venta": En el caso de una venta de Mercado Libre, poner el correspondiente a la venta analizada. Caso contrario, dejar el campo con un "0"
                18. "costo_envio": Dejar este campo en blanco para todas las ventas, sin importar el canal de venta.
                19. "ibb": Detectar, en caso de una venta efectuada en Mercado Libre, el Impuesto de Ingresos Brutos correspondiente a la venta analizada. Caso contrario,
                dejar el campo en "0".
                
                Ejemplo de salida:
                {
                "fecha": "04/05/2026",
                "canal_venta": "ML",
                "entregado": "NO",
                "cantidad": "2",
                "producto": "200 KG",
                "nombre_razon_social": "NORA ANA SCHERVA",
                "numero_op": "2000016129420630",
                "numero_fc". "",
                "direccion": "",
                "horario": "",
                "dni_cuit": "17541248"
                "cobro_flete": "0",
                "medio_pago": "MP",
                "comentarios": "",
                "pago": "SI",
                "valor_venta": "659998",
                "cargo_venta": "92399.72",
                "costo_envio": "0",
                "ibb": "3959.99"
                }
    """

def init_ai_api(ruta_env):
    try:
        print("Activando la API de la IA...")
        load_dotenv(dotenv_path=ruta_env)
        print("API activada correctamente")
        return genai.Client()
    except Exception as e:
        print(f"Error: {e}")
        return None

def parsear_data_reporte(directorio, client):
    try:
        archivo_subido = client.files.upload(file=directorio)
    except Exception as e:
        print(f"Error al subir el archivo: {e}")
        return None

    for intento in range(REINTENTOS):
        try:
            respuesta = client.models.generate_content(
                        model=MODELO_AI,
                        contents=[archivo_subido, PROMPT]
                        )
            raw_text = respuesta.text.replace('```json', '').replace('```', '').strip()
            print("Texto extraido por la IA exitosamente")
            return json.loads(raw_text)
        
        except ResourceExhausted as e:
            print(f"Límite de cuota alcanzado. Esperando 30 segundos antes del reintento {intento + 1}/{REINTENTOS}...")
            time.sleep(30)
            
        except Exception as e:
            print(f"Error: {e}")
            break
            
    print("No se pudo procesar el documento después de varios intentos.")
    return None
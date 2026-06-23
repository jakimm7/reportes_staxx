import time
import json
import google.genai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

MODELO_AI = "gemini-2.5-flash"
REINTENTOS = 3
PROMPT =  """Analiza este documento de venta y extrae únicamente los siguientes datos en formato JSON estricto. 
                No apliques ninguna lógica adicional ni devuelvas campos que no se solicitan.

                1. "canal": En caso de tratarse de una orden de compra de mercado libre o screenshot con una venta de la página, completa el campo con la leyenda "ML". En
                caso de que fuera una factura A, dejar el campo con la leyenda "VENDEDOR".
                2. "producto": En caso de que se haya vendido una estanteria de 300 KG por estante o 1200 KG en total, completa el campo con la leyenda "300 KG". Caso contrario
                debes dejar el mismo con la salida "200 KG".
                3. "cantidad": Aquí debes de detallar la cantidad de estanterías que se vendieron en el reporte analizado.
                4. "num_op": Si el pedido analizado es de Mercado Libre, completa con el número de orden de compra asociado al mismo. Es importante dejar el campo en blanco en caso
                de tratarse de un reporte asociado a una Factura A.
                5. "num_fc": Si el pedido analizado es de una Factura A, completa con el número de factura asociado a la misma. Es importante dejar el campo en blanco en caso
                de tratarse de un reporte asociado a una venta por Mercado Libre.
                6. "fecha": Completa este campo con la fecha asociada a la compra, ya sea de Mercado Libre o a la correspondiente fecha de facturación en caso de tratarse una homónima.
                Es importante especificar la fecha con el formato dd/mm/aa (día, mes, año).
                7. "tipo_cambio": Para los dos tipos de canales de venta, se debe dejar este campo vacío.
                8. "nombre_razon_social": Si se trata de una venta de Mercado Libre, rastrea si existe alguna razon social asociada a la misma. Si no se econtrase, completar con el
                nombre completo de la persona que realizo el pedido. En caso de una factura A, siempre utilizar la razon social a la cual se factura la misma.
                9. "datos_facturacion": Para ambos canales de ventas, analiza y busca un CUIT, dirección fiscal y razón social/nombre. Si alguno de los datos no se encuentran en el
                reporte analizado, completar con los datos que se encuentren o dejar en blanco si no se encuentra ninguno.
                10. "dni_cuit": Completar con el CUIT de la razon social a la que se factura o el mismo que se encuentra asociado a la venta por Mercado Libre. Si no se encontrase un 
                CUIT asociado a la venta, dejar el campo con el DNI de la persona a la cual efectuo la compra según el reporte.
                11. "forma_pago": Solo si la venta es por Mercado Libre, completar el campo con la leyenda "Mercado Pago". Caso contrario, dejar el campo vacío.
                12. "pago": Solo si la venta es por Mercado Libre, completar el campo con la leyenda "SI". Caso contrario, sobreescribir el mismo con el texto "NO".
                13. "valor_venta": Para ambos canales de venta, ya sea Mercado Libre o una factura A, debes completarlo con el VALOR FINAL de la venta (es decir, con IVA incluído en
                caso de tratarse de una Factura A. Para las ventas de Mercado Libre, simplemente utilizar el monto total por el cual se realizo la venta).
                14. "cargo_venta": Si es una venta por Mercado Libre, completar con el cargo que realiza la plataforma a la hora de realizarse una venta por la misma. Dejar en 0 para
                el caso de las ventas realizadas por factura A.
                15. "ibb": Si es una venta por Mercado Libre, completar con el impuesto de Ingresos Brutos correspondiente a la venta, detallado por el reporte. Dejar en 0 para
                el caso de las ventas realizadas por factura A.
                16. "iva": Si es una venta que fue facturada, completar con el apartado del total de IVA en la parte inferior de la misma. Caso contrario, dejar el campo en 0.
                17. "valor_neto": Si es una venta que fue facturada, completar con el apartado del total NETO en la parte inferior de la misma. Caso contrario, dejar el campo en 0.
                
                NO OLVIDES NO USAR COMAS PARA LOS SEPARADOR DE MILES DE LOS NUMEROS, SOLO PUNTOS PARA LOS DECIMALES.

                Ejemplo de salida de una venta de Mercado Libre:
                {
                "canal": "Mercado Libre",
                "producto": "200 KG",
                "cantidad": "1",
                "num_op": "2000016301904764",
                "num_fc": "",
                "fecha": "6/5/2026",
                "tipo_cambio": "",
                "nombre_razon_social": "Diego Gastón Diomede",
                "datos_facturacion": "Diego Gastón Diomede - DNI 24152630 - Calle 25 de Mayo 775, Córdoba - CP: 5004",
                "dni_cuit": "24152630",
                "forma_pago": "Mercado Pago",
                "pago": "SI",
                "valor_venta": "368350",
                "cargo_venta": "51569",
                "ibb": "7735.35",
                "iva": "0",
                "valor_neto": "0"
                }

                Ejemplo de salida de una venta facturada:
                {
                "canal": "VENDEDOR",
                "producto": "200 KG",
                "cantidad": "5",
                "num_op": "",
                "num_fc": "0010-00001482",
                "fecha": "5/5/2026",
                "tipo_cambio": "",
                "nombre_razon_social": "COLMAN, ADRIAN KEVIN",
                "datos_facturacion": "Adrián Kevin Colman - CUIT 20368972909 - Cordoba 33, Gualeguaychú",
                "dni_cuit": "20368972909",
                "forma_pago": "",
                "pago": "NO",
                "valor_venta": "1417500",
                "cargo_venta": "0",
                "ibb": "0",
                "iva": "246012.4",
                "valor_neto": "1171487.6"
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
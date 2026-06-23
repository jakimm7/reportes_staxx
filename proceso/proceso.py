import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.formula.translate import Translator
from datetime import datetime
from utils.utils import dict_to_array, copiar_estilo

CANTIDAD = "cantidad"
FECHA = "fecha"
TC = "tipo_cambio"
VALOR_VENTA = "valor_venta"
CARGO_VENTA = "cargo_venta"
COSTO_ENVIO = "costo_envio"
IBB = "ibb"
VALOR_NETO = "valor_neto"
IVA = "iva"
COSTO_IMPORTACION = "costo_importacion"
COSTO_ADMIN = "costo_admin"
CANAL = "canal"
PRODUCTO = "producto"
COMISION_VENDEDOR = "costo_vendedor"

PLATAFORMA_E_COMMERCE = "ML"
ESTANTERIA_200 = "200 KG"
ESTANTERIA_300 = "300 KG"

FORMATO_FECHA = "%d/%m/%Y"

COSTO_200 = 65.58
COSTO_300 = 87.17

ALICUOTA_IVA = 1.21
ALICUOTA_COSTO_ADMIN = 0.07
ALICUOTA_COMISION = 0.04

COLUMNAS_FORMULAS = 4

def procesar_data(datos_venta, tc_venta):
    datos_venta[CANTIDAD] = int(datos_venta[CANTIDAD])
    datos_venta[FECHA] = datetime.strptime(datos_venta[FECHA], FORMATO_FECHA).strftime(FORMATO_FECHA)
    datos_venta[TC] = tc_venta
    datos_venta[VALOR_VENTA] = float(datos_venta[VALOR_VENTA])
    datos_venta[CARGO_VENTA] = float(datos_venta[CARGO_VENTA])
    datos_venta[COSTO_ENVIO] = 0
    datos_venta[IBB] = float(datos_venta[IBB])

    if datos_venta[CANAL] == PLATAFORMA_E_COMMERCE:
        datos_venta[VALOR_NETO] = (datos_venta[VALOR_VENTA] / ALICUOTA_IVA) - datos_venta[IBB]
        datos_venta[IVA] = datos_venta[VALOR_VENTA] - datos_venta[VALOR_NETO]
    else:
        datos_venta[VALOR_NETO] = float(datos_venta[VALOR_NETO])
        datos_venta[IVA] = float(datos_venta[IVA])
    
    costo_impo_usd = 0
    if datos_venta[PRODUCTO] == ESTANTERIA_200:
        costo_impo_usd = COSTO_200
    else:
        costo_impo_usd = COSTO_300
    
    datos_venta[COSTO_IMPORTACION] = (costo_impo_usd * tc_venta) * datos_venta[CANTIDAD]
    datos_venta[COSTO_ADMIN] = datos_venta[COSTO_IMPORTACION] * ALICUOTA_COSTO_ADMIN
    datos_venta[COMISION_VENDEDOR] = datos_venta[VALOR_NETO] * ALICUOTA_COMISION

    return dict_to_array(datos_venta)

def transcribir_excel(ruta_excel, datos_venta, mes):
    libro = openpyxl.load_workbook(ruta_excel)
    nombre_tabla = f"VENTAS_{mes}"
    ws = None
    tabla = None
    hojas_a_buscar = [libro[mes]] if mes else libro.worksheets

    for hoja_actual in hojas_a_buscar:
        if nombre_tabla in hoja_actual.tables:
            ws = hoja_actual
            tabla = hoja_actual.tables[nombre_tabla]
            break

    if tabla is None:
        raise ValueError(f"No se encontró la tabla '{nombre_tabla}' en el archivo.")

    rango_actual = tabla.ref
    col_inicio, fila_inicio, col_fin, fila_fin = openpyxl.utils.cell.range_boundaries(rango_actual)

    fila_anterior = fila_fin
    nueva_fila = fila_fin + 1
    col_inicio_formulas = col_fin - COLUMNAS_FORMULAS + 1

    for i, valor in enumerate(datos_venta):
        col = col_inicio + i
        if col >= col_inicio_formulas:
            break
        celda_origen = ws.cell(row=fila_anterior, column=col)
        celda_destino = ws.cell(row=nueva_fila, column=col)
        celda_destino.value = valor
        copiar_estilo(celda_origen, celda_destino)

    for col in range(col_inicio_formulas, col_fin + 1):
        letra = get_column_letter(col)
        celda_origen = ws.cell(row=fila_anterior, column=col)
        celda_destino = ws.cell(row=nueva_fila, column=col)
        copiar_estilo(celda_origen, celda_destino)

        if isinstance(celda_origen.value, str) and celda_origen.value.startswith("="):
            formula_traducida = Translator(
                celda_origen.value,
                origin=f"{letra}{fila_anterior}"
            ).translate_formula(f"{letra}{nueva_fila}")
            celda_destino.value = formula_traducida

    nuevo_rango = f"{get_column_letter(col_inicio)}{fila_inicio}:{get_column_letter(col_fin)}{nueva_fila}"
    tabla.ref = nuevo_rango

    libro.save(ruta_excel)

import os
import unittest
from parse_ai.parse_ai import init_ai_api, parsear_data_reporte
from proceso.proceso import procesar_data
from db.db import init_sales_db, cargar_venta
from utils.utils import cargar_tipo_cambio

DIRECTORIO_PRUEBA = "./test_reports"

NUM_OP_FC_PRUEBA = ["2000016339827728", "2000016289757078", "2000016289757078", "2000016424780216", "2000016349828892", "2000016525678730", "2000016445037520"
                    "2000016268270524", "2000016332909340", "0010-00001474", "0010-00001631", "0010-00001482", "0010-00001563", "2000016426848572", "0010-00001533"
                    "2000016378750466", "2000016378720372", "2000016543881542", "2000016561236124", "2000016355100342", "2000016534076582", "2000016344169930"
                    "0010-00001501", "0010-00001488", "2000016613113522", "2000016270934428", "2000016373518768", "0010-00001528", "2000016299824408"
                    "2000016482652964", "2000016232668232", "2000016317610278", "2000016392859248", "2000016454123380", "2000016363175154", "2000016406790130"
                    "2000016564354534", "2000016265718314", "0010-00001551", "2000016437881574", "2000016375329598", "2000016391462318", "2000012938510141", "2000016391826752"]

class TestParsearData(unittest.TestCase):
    def testParseAI(self):
        client = init_ai_api()
        init_sales_db()
        _, tc_venta = cargar_tipo_cambio()

        for reporte in os.listdir(DIRECTORIO_PRUEBA):
            data_parseada = parsear_data_reporte(reporte, client)
            datos_venta = procesar_data(data_parseada, tc_venta)
            cargar_venta(datos_venta)

        
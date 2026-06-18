import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

RUTA_SALES = Path("/srv/reportes_staxx/db/sales.db")

CANAL = 0
PRODUCTO = 1
CANTIDAD = 2
NUM_OP = 3
NUM_FC = 4
FECHA = 5
TIPO_CAMBIO = 6
RAZON_SOCIAL = 7
DATOS_FACTURACION = 8
DNI_CUIT = 9
FORMA_PAGO = 10
PAGO = 11
VALOR_VENTA = 12
CARGO_VENTA = 13
IBB = 14
IVA = 15
VALOR_NETO = 16
COSTO_IMPO = 17
COSTO_ADMIN = 18
COMISION = 19

def init_sales_db():
    try:
        RUTA_SALES.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(RUTA_SALES)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                cargada_excel TEXT DEFAULT 'NO',
                canal TEXT,
                entregado TEXT DEFAULT 'NO',
                armado TEXT DEFAULT 'NO',
                producto TEXT,
                cantidad INT,
                numero_op TEXT,
                numero_fc TEXT,
                fecha DATE,
                tipo_cambio FLOAT,
                razon_social TEXT,
                direccion TEXT DEFAULT '',
                horario TEXT DEFAULT '',
                datos_facturacion TEXT,
                dni_cuit TEXT,
                cobro_flete FLOAT DEFAULT 0.0,
                forma_pago TEXT,
                comentarios TEXT DEFAULT '',
                pago TEXT,
                valor_venta FLOAT,
                cargo_venta FLOAT,
                costo_envio FLOAT DEFAULT 0.0,
                ibb FLOAT,
                iva FLOAT,
                neto FLOAT,
                costo_impo FLOAT,
                costo_admin FLOAT,
                comision FLOAT,
                PRIMARY KEY (numero_op, numero_fc)
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Base de datos de ventas y tablas creadas exitosamente.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al crear la base de datos de ventas: {e}")

def cargar_venta(datos):
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO ventas (canal, producto, cantidad, numero_op, numero_fc, fecha, tipo_cambio, 
                   razon_social, datos_facturacion, dni_cuit, forma_pago, pago, valor_venta, cargo_venta, ibb,
                    iva, neto, costo_impo, costo_admin, comision)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(numero_op, numero_fc) DO UPDATE SET
            canal             = excluded.canal,
            producto          = excluded.producto,
            cantidad          = excluded.cantidad,
            numero_op         = excluded.numero_op,
            numero_fc         = excluded.numero_fc,
            fecha             = excluded.fecha,
            tipo_cambio       = excluded.tipo_cambio,
            razon_social      = excluded.razon_social,
            datos_facturacion = excluded.datos_facturacion,
            dni_cuit          = excluded.dni_cuit,
            forma_pago        = excluded.forma_pago,
            pago              = excluded.pago,
            valor_venta       = excluded.valor_venta,
            cargo_venta       = excluded.cargo_venta,
            ibb               = excluded.ibb,
            iva               = excluded.iva,
            neto              = excluded.neto,
            costo_impo        = excluded.costo_impo,
            costo_admin       = excluded.costo_admin,
            comision          = excluded.comision
    ''', (
        datos[CANAL], datos[PRODUCTO], datos[CANTIDAD], datos[NUM_OP], datos[NUM_FC], datos[FECHA], datos[TIPO_CAMBIO], datos[RAZON_SOCIAL], datos[DATOS_FACTURACION],
        datos[DNI_CUIT], datos[FORMA_PAGO], datos[PAGO], datos[VALOR_VENTA], datos[CARGO_VENTA], datos[IBB], datos[IVA], datos[VALOR_NETO], datos[COSTO_IMPO],
        datos[COSTO_ADMIN], datos[COMISION]
    ))

    conn.commit()
    conn.close()

def obtener_ventas_nuevas():
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT canal, entregado, armado, producto, cantidad, numero_op, numero_fc, fecha, tipo_cambio,
                razon_social, direccion, horario, datos_facturacion, dni_cuit, cobro_flete, forma_pago,
                comentarios, pago, valor_venta, cargo_venta, costo_envio, ibb, iva, neto, costo_impo,
                costo_admin, comision
        FROM ventas
        WHERE cargada_excel = 'NO'
        ORDER BY ROWID
    ''')

    ventas = [list(fila) for fila in cursor.fetchall()]
    conn.close()
    return ventas
    
def marcar_venta_cargada(claves):
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()
    cursor.executemany('''
        UPDATE ventas SET cargada_excel = 'SI'
        WHERE numero_op = ? AND numero_fc = ?
    ''', claves)
    conn.commit()
    conn.close()
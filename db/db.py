import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

RUTA_SALES = Path("srv/reportes_staxx/db/sales.db")

FECHA = 0
TC = 1
CANAL = 2
CANTIDAD = 3
PRODUCTO = 4
RAZON_SOCIAL = 5
NUMERO_OP_FC = 6
DNI_CUIT = 7
FORMA_PAGO = 8
VALOR_VENTA = 9
CARGO_VENTA = 10
IBB = 11
IVA = 12
NETO = 13
COSTO_ADMIN = 14
COMISION = 15
COSTO_IMPO = 16

def init_sales_db():
    try:
        RUTA_SALES.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(RUTA_SALES)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                cargada_excel TEXT DEFAULT 'NO',
                fecha DATE,
                canal TEXT,
                cantidad INT,
                producto TEXT,
                razon_social TEXT,
                numero_op_fc TEXT PRIMARY KEY,
                dni_cuit TEXT,
                forma_pago TEXT,
                valor_venta FLOAT,
                cargo_venta FLOAT,
                ibb FLOAT,
                iva FLOAT,
                neto FLOAT,
                costo_admin FLOAT,
                comision FLOAT,
                costo_impo FLOAT          
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
        INSERT INTO ventas (canal, cantidad, producto, razon_social, numero_op_fc,
                            dni_cuit, forma_pago, valor_venta, cargo_venta, ibb,
                            iva, neto, costo_admin, comision, costo_impo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(numero_op_fc) DO UPDATE SET
            fecha        = excluded.fecha,
            canal        = excluded.canal,
            cantidad     = excluded.cantidad,
            producto     = excluded.producto,
            razon_social = excluded.razon_social,
            dni_cuit     = excluded.dni_cuit,
            forma_pago   = excluded.forma_pago,
            valor_venta  = excluded.valor_venta,
            cargo_venta  = excluded.cargo_venta,
            ibb          = excluded.ibb,
            iva          = excluded.iva,
            neto         = excluded.neto,
            costo_admin  = excluded.costo_admin,
            comision     = excluded.comision,
            costo_impo   = excluded.costo_impo
    ''', (
        datos[FECHA], datos[CANAL], datos[CANTIDAD], datos[PRODUCTO], datos[RAZON_SOCIAL],
        datos[NUMERO_OP_FC], datos[DNI_CUIT], datos[FORMA_PAGO],
        datos[VALOR_VENTA], datos[CARGO_VENTA], datos[IBB], datos[IVA],
        datos[NETO], datos[COSTO_ADMIN], datos[COMISION], datos[COSTO_IMPO]
    ))

    conn.commit()
    conn.close()

def obtener_ventas_nuevas():
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT canal, cantidad, producto, razon_social, numero_op_fc,
               dni_cuit, forma_pago, valor_venta, cargo_venta, ibb,
               iva, neto, costo_admin, comision, costo_impo
        FROM ventas
        WHERE cargada_excel = 'NO'
        ORDER BY ROWID
    ''')

    ventas = [list(fila) for fila in cursor.fetchall()]
    conn.close()
    return ventas
    
def marcar_venta_cargada(numeros_op_fc):
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()

    cursor.executemany('''
        UPDATE ventas SET cargada = 'SI'
        WHERE numero_op_fc = ?
    ''', [(numero,) for numero in numeros_op_fc])

    conn.commit()
    conn.close()
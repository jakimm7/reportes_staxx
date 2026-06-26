import sqlite3
from datetime import datetime
from pathlib import Path

RUTA_SALES = Path("/srv/reportes_staxx/db/sales.db")

POS_CANAL = 0
POS_PRODUCTO = 1
POS_CANTIDAD = 2
POS_NUM_OP = 3
POS_NUM_FC = 4
POS_FECHA = 5
POS_NOMBRE = 6
POS_DATOS_FACTURACION = 7
POS_DNI = 8
POS_FORMA_PAGO = 9
POS_COMENTARIOS = 10
POS_PAGO = 11
POS_TC = 12
POS_VALOR_VENTA = 13
POS_CARGO_VENTA = 14
POS_IBB = 15
POS_IVA = 16
POS_VALOR_NETO = 17
POS_COSTO_ADMIN = 18
POS_COMISION = 19
POS_COSTO_IMPO = 20

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
                costo_admin FLOAT,
                comision FLOAT,
                costo_impo FLOAT,
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
            razon_social      = excluded.razon_social,
            datos_facturacion = excluded.datos_facturacion,
            dni_cuit          = excluded.dni_cuit,
            forma_pago        = excluded.forma_pago,
            pago              = excluded.pago,
            tipo_cambio       = excluded.tipo_cambio,
            valor_venta       = excluded.valor_venta,
            cargo_venta       = excluded.cargo_venta,
            ibb               = excluded.ibb,
            iva               = excluded.iva,
            neto              = excluded.neto,
            costo_admin       = excluded.costo_admin,
            comision          = excluded.comision
            costo_impo        = excluded.costo_impo
    ''', (
        datos[POS_CANAL], datos[POS_PRODUCTO], datos[POS_CANTIDAD], datos[POS_NUM_OP], datos[POS_NUM_FC], datos[POS_FECHA], datos[POS_NOMBRE], datos[POS_DATOS_FACTURACION],
        datos[POS_DNI], datos[POS_FORMA_PAGO], datos[POS_PAGO], datos[POS_TC], datos[POS_VALOR_VENTA], datos[POS_CARGO_VENTA], datos[POS_IBB], datos[POS_IVA], datos[POS_VALOR_NETO],
        datos[POS_COSTO_ADMIN], datos[POS_COMISION], datos[POS_COSTO_IMPO]
    ))

    conn.commit()
    conn.close()

def obtener_ventas_nuevas():
    conn = sqlite3.connect(RUTA_SALES)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT canal, entregado, armado, producto, cantidad, numero_op, numero_fc, fecha, razon_social,
                direccion, horario, datos_facturacion, dni_cuit, cobro_flete, forma_pago, comentarios,
                pago, tipo_cambio, valor_venta, cargo_venta, costo_envio, ibb, iva, neto,costo_admin, 
                comision, costo_impo
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
    cursor.execute('''
        UPDATE ventas SET cargada_excel = 'SI'
        WHERE numero_op = ? AND numero_fc = ?
    ''', claves)
    conn.commit()
    conn.close()
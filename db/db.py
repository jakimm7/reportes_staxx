import sqlite3
from datetime import datetime

RUTA_DB = "/srv/reportes_staxx/db/tracking.db"

def init_db():
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            archivo TEXT PRIMARY KEY,
            estado TEXT,
            fecha TEXT
        )
    ''')
    conn.commit()
    conn.close()

def actualizar_estado(archivo, estado):
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO facturas (archivo, estado, fecha)
        VALUES (?, ?, ?)
        ON CONFLICT(archivo) DO UPDATE SET
        estado=excluded.estado,
        fecha=excluded.fecha
    ''', (archivo, estado, ahora))
    
    conn.commit()
    conn.close()
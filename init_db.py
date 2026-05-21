import sqlite3
import os

DB_NAME = "turnoya.db"

def inicializar_base_datos():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tabla Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            fecha_registro TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # 2. Tabla Servicios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_servicio TEXT NOT NULL,
            duracion_minutos INTEGER NOT NULL,
            precio REAL NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')

    # 3. Tabla Citas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL,
            observaciones TEXT,
            fecha_creacion TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio)
        )
    ''')

    # 4. Tabla Incidencias Calidad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidencias_calidad (
            id_incidencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cita INTEGER,
            tipo_incidencia TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            criterio_iso TEXT NOT NULL,
            severidad TEXT NOT NULL,
            fecha_reporte TEXT DEFAULT (datetime('now', 'localtime')),
            estado TEXT NOT NULL,
            FOREIGN KEY (id_cita) REFERENCES citas(id_cita)
        )
    ''')

    # Datos iniciales de prueba
    cursor.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES ('Juan Pérez', '3157778899', 'juan.perez@email.com')")

    servicios_iniciales = [
        ('Corte de Cabello', 30, 25000.0, 1),
        ('Barbería', 25, 20000.0, 1),
        ('Manicure', 45, 18000.0, 1),
        ('Cepillado', 40, 22000.0, 1),
        ('Limpieza Facial', 60, 45000.0, 1)
    ]
    cursor.executemany("INSERT INTO servicios (nombre_servicio, duracion_minutos, precio, activo) VALUES (?, ?, ?, ?)", servicios_iniciales)

    conn.commit()
    conn.close()
    print("¡Base de datos 'turnoya.db' inicializada con éxito!")

if __name__ == "__main__":
    inicializar_base_datos()
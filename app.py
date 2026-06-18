import streamlit as st
import sqlite3
import pandas as pd
import time
import os
from datetime import datetime

DB_NAME = "turnoya.db"

# --- BLINDAJE ABSOLUTO PARA DESPLIEGUES EN LA NUBE (Streamlit Cloud) ---
def garantizar_base_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Crear tablas usando estructuras seguras IF NOT EXISTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            fecha_registro TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_servicio TEXT NOT NULL,
            duracion_minutos INTEGER NOT NULL,
            precio REAL NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')

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

    # 2. Control estricto de Datos Semilla (Evita duplicados en refrescos)
    # Solo insertamos si la tabla servicios está vacía
    cursor.execute("SELECT COUNT(*) FROM servicios")
    if cursor.fetchone()[0] == 0:
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

# Forzar la ejecución segura de la estructura base
garantizar_base_datos()
# ----------------------------------------------------------------------
        



def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

st.set_page_config(page_title="TurnoYa Lab", page_icon="📅", layout="wide")
st.title("📅 TurnoYa Lab — Sistema de Agendamiento")
st.caption("Entorno de Laboratorio de Calidad de Software (Versión 1.0 - Con Fallas Controladas)")

tabs = st.tabs([
    "👥 Gestión de Clientes", 
    "💅 Servicios Disponibles", 
    "✏️ Registrar Cita", 
    "📖 Consulta de Agenda", 
    "📊 Métricas de Calidad"
])

# MÓDULO 1: GESTIÓN DE CLIENTES
with tabs[0]:
    st.header("Módulo 1: Registro de Clientes")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nuevo Registro")
        nombre = st.text_input("Nombre del Cliente")
        telefono = st.text_input("Teléfono")
        correo = st.text_input("Correo Electrónico")
        
        if st.button("Guardar Cliente"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES (?, ?, ?)", (nombre, telefono, correo))
            conn.commit()
            conn.close()
            st.success(f"Cliente '{nombre}' registrado.")
    with col2:
        st.subheader("Clientes en Sistema")
        conn = get_db_connection()
        df_clientes = pd.read_sql_query("SELECT id_cliente, nombre, telefono, correo FROM clientes", conn)
        conn.close()
        st.dataframe(df_clientes, use_container_width=True)

# MÓDULO 2: GESTIÓN DE SERVICIOS
with tabs[1]:
    st.header("Módulo 2: Catálogo de Servicios")
    st.info("Nota del Sistema: Los servicios están protegidos de fábrica. No pueden modificarse desde la UI.")
    conn = get_db_connection()
    df_servicios = pd.read_sql_query("SELECT id_servicio, nombre_servicio, duracion_minutos, precio FROM servicios WHERE activo = 1", conn)
    conn.close()
    st.table(df_servicios)

# MÓDULO 3: GESTIÓN DE CITAS
with tabs[2]:
    st.header("Módulo 3: Creación de Citas")
    conn = get_db_connection()
    clientes_list = conn.execute("SELECT id_cliente, nombre FROM clientes").fetchall()
    servicios_list = conn.execute("SELECT id_servicio, nombre_servicio FROM servicios").fetchall()
    conn.close()
    
    dict_clientes = {c['nombre']: c['id_cliente'] for c in clientes_list}
    dict_servicios = {s['nombre_servicio']: s['id_servicio'] for s in servicios_list}
    
    if not dict_clientes:
        st.warning("⚠️ No existen clientes registrados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            sel_cliente = st.selectbox("Seleccione el Cliente", list(dict_clientes.keys()))
            sel_servicio = st.selectbox("Seleccione el Servicio", list(dict_servicios.keys()))
            fecha_cita = st.date_input("Fecha de la Cita", datetime.now())
            hora_cita = st.time_input("Hora de la Cita")
            observaciones = st.text_area("Observaciones Adicionales")
        with col2:
            st.subheader("Estado Base de la Cita")
            estado_fijo = "Pendiente"
            st.code(f"Estado automático: {estado_fijo}")
            
            if st.button("Agendar Cita"):
                id_c = dict_clientes[sel_cliente]
                id_s = dict_servicios[sel_servicio]
                f_str = fecha_cita.strftime("%Y-%m-%d")
                h_str = hora_cita.strftime("%H:%M")
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO citas (id_cliente, id_servicio, fecha, hora, estado, observaciones) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_c, id_s, f_str, h_str, estado_fijo, observaciones)
                )
                conn.commit()
                conn.close()
                st.success(f"Cita procesada para el {f_str} a las {h_str}.")

# MÓDULO 4: CONSULTA DE AGENDA
with tabs[3]:
    st.header("Módulo 4: Visualización de Agenda Completa")
    start_time = time.time()
    
    conn = get_db_connection()
    query_agenda = """
        SELECT c.id_cita, cl.nombre AS cliente, s.nombre_servicio AS servicio, c.fecha, c.hora, c.estado 
        FROM citas c
        JOIN clientes cl ON c.id_cliente = cl.id_cliente
        JOIN servicios s ON c.id_servicio = s.id_servicio
    """
    df_agenda = pd.read_sql_query(query_agenda, conn)
    conn.close()
    
    retraso_base = 1.5 
    penalizacion_volumen = len(df_agenda) * 0.1
    time.sleep(retraso_base + penalizacion_volumen) 
    
    tiempo_carga = time.time() - start_time
    st.metric(label="⏱️ Tiempo de Respuesta del Servidor", value=f"{tiempo_carga:.3f} segundos")
    st.dataframe(df_agenda, use_container_width=True)

# MÓDULO 5: MÉTRICAS DE CALIDAD
with tabs[4]:
    st.header("Módulo 5: Tablero de Control de Calidad e Incidencias")
    conn = get_db_connection()
    total_citas = conn.execute("SELECT COUNT(*) FROM citas").fetchone()[0]
    citas_pendientes = conn.execute("SELECT COUNT(*) FROM citas WHERE estado = 'Pendiente'").fetchone()[0]
    citas_duplicadas = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT id_cliente, fecha, hora FROM citas 
            GROUP BY id_cliente, fecha, hora HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    clientes_sin_tel = conn.execute("SELECT COUNT(*) FROM clientes WHERE telefono = '' OR telefono IS NULL").fetchone()[0]
    conn.close()
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Citas", total_citas)
    m_col2.metric("Citas Duplicadas", citas_duplicadas, delta="Crítico", delta_color="inverse")
    m_col3.metric("Clientes sin Teléfono", clientes_sin_tel, delta="Usabilidad", delta_color="off")
    m_col4.metric("Citas Pendientes", citas_pendientes)

    st.markdown("---")
    st.subheader("🛠️ Bitácora de Registro de Incidencias de Calidad (ISO/IEC 25010)")
    col_inc1, col_inc2 = st.columns(2)
    with col_inc1:
        tipo_i = st.selectbox("Tipo de Defecto", ["Citas Duplicadas", "Validación Nula", "Rendimiento/Lentitud", "Defecto de Interfaz", "Código Rígido"])
        desc_i = st.text_area("Evidencia Técnica / Descripción")
        crit_iso = st.selectbox("Criterio ISO 25010", ["Adecuación Funcional", "Eficiencia de Desempeño", "Usabilidad", "Confiabilidad", "Mantenibilidad"])
    with col_inc2:
        severidad_i = st.select_slider("Severidad", options=["Baja", "Media", "Alta", "Crítica"])
        estado_i = st.selectbox("Estado", ["Abierta", "En Análisis", "Corregida"])
        
        if st.button("Insertar Incidencia"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO incidencias_calidad (tipo_incidencia, descripcion, criterio_iso, severidad, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo_i, desc_i, crit_iso, severidad_i, estado_i))
            conn.commit()
            conn.close()
            st.success("Incidencia documentada.")
            
    st.subheader("📋 Historial de Auditorías de Calidad Realizadas")
    conn = get_db_connection()
    df_incidencias = pd.read_sql_query("SELECT id_incidencia, tipo_incidencia, descripcion, criterio_iso, severidad, estado FROM incidencias_calidad", conn)
    conn.close()
    st.dataframe(df_incidencias, use_container_width=True)
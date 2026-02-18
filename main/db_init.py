import os
import sqlite3
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Crear tablas
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        fecha_registro DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS insumos (
        id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        unidad_medida TEXT,
        costo_unitario REAL DEFAULT 0,
        stock_actual REAL DEFAULT 0,
        fecha_actualizacion DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        fecha_anticipo DATE DEFAULT CURRENT_DATE,
        fecha_entrega DATE DEFAULT CURRENT_DATE,
        estado TEXT DEFAULT 'pendiente',
        total REAL,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    );

    CREATE TABLE IF NOT EXISTS detalle_pedido (
        id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pedido INTEGER NOT NULL,
        id_insumo INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL,
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
        FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo)
    );

    CREATE TABLE IF NOT EXISTS gastos (
        id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT NOT NULL,
        categoria TEXT,
        monto REAL NOT NULL,
        fecha DATE DEFAULT CURRENT_DATE,
        pagado_a TEXT,
        medio_pago TEXT
    );

    CREATE TABLE IF NOT EXISTS facturas (
        id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pedido INTEGER NOT NULL,
        tipo TEXT NOT NULL,  -- 'anticipo' o 'saldo'
        monto REAL NOT NULL,
        fecha_programada DATE NOT NULL,  -- fecha esperada de pago
        fecha_pago DATE,  -- fecha real de pago
        medio_pago TEXT,
        cuenta_receptora TEXT,
        pagado_por TEXT,
        estado TEXT DEFAULT 'pendiente',  -- pendiente, pagado, vencido
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
    );
    """)

    # 2. Limpiar datos previos (opcional, para reinicializar con los simulados)
    cursor.executescript("""
        DELETE FROM detalle_pedido;
        DELETE FROM facturas;
        DELETE FROM gastos;
        DELETE FROM pedidos;
        DELETE FROM clientes;
        DELETE FROM insumos;
    """)

    # 3. Insertar datos simulados

    # --- clientes --- [file:1]
    clientes = [
        (1, "Arturo", "2587125", "arturo@email.com", "Cali Centro", "2026-01-11"),
        (2, "Beatriz", "3101234567", "beatriz@email.com", "San Alejo", "2025-08-29"),
        (3, "Carlos", "3212345678", "carlos@email.com", "Pance", "2025-08-07"),
        (4, "Diana", "3159876543", "diana@email.com", "Comuna 1", "2026-02-06"),
        (5, "Enrique", "3187654321", "enrique@email.com", "Comuna 2", "2025-10-10"),
        (6, "Fernanda", "3165432109", "fernanda@email.com", "San Fernando", "2025-10-02"),
        (7, "Gabriel", "3143210987", "gabriel@email.com", "Bolívar", "2025-09-27"),
        (8, "Herminia", "3121098765", "herminia@email.com", "Meléndez", "2025-09-05"),
        (9, "Ignacio", "3109876543", "ignacio@email.com", "Cucarachita", "2026-02-05"),
        (10, "Juana", "3187654320", "juana@email.com", "Alameda", "2025-08-27"),
        (11, "Kamila", "3165432100", "kamila@email.com", "La Floresta", "2026-01-21"),
        (12, "Leonardo", "3143210980", "leonardo@email.com", "Siloe", "2026-02-06"),
        (13, "Mariana", "3121098760", "mariana@email.com", "Aguablanca", "2025-12-18"),
        (14, "Nicolás", "3109876540", "nicolas@email.com", "Laguna", "2025-08-23"),
        (15, "Olivia", "3187654310", "olivia@email.com", "Puerto Isaacs", "2025-12-30"),
    ]
    cursor.executemany("""
        INSERT INTO clientes (id_cliente, nombre, telefono, email, direccion, fecha_registro)
        VALUES (?, ?, ?, ?, ?, ?)
    """, clientes)

    # --- insumos --- [file:1]
    insumos = [
        (1, "botón", "UND", 1000, 50, "2026-02-17"),
        (2, "tela algodón", "metro", 5000, 25, "2026-02-17"),
        (3, "hilo blanco", "carrete", 800, 15, "2026-02-17"),
        (4, "cremallera", "UND", 2000, 40, "2026-02-17"),
        (5, "elástico", "metro", 1500, 30, "2026-02-17"),
        (6, "etiqueta", "UND", 500, 100, "2026-02-17"),
        (7, "aguja", "caja", 2500, 20, "2026-02-17"),
        (8, "goma", "metro", 1200, 35, "2026-02-17"),
        (9, "cinta", "metro", 800, 45, "2026-02-17"),
        (10, "pintura", "litro", 8000, 8, "2026-02-17"),
    ]
    cursor.executemany("""
        INSERT INTO insumos (id_insumo, nombre, unidad_medida, costo_unitario, stock_actual, fecha_actualizacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """, insumos)

    # --- pedidos --- (extracto del archivo, puedes seguir completando la lista si quieres todos) [file:1]
    pedidos = [
        (1, 7, "2026-02-03", "2026-02-19", "cancelado", 227500),
        (2, 1, "2025-11-26", "2025-12-16", "cancelado", 56500),
        (3, 1, "2025-12-16", "2025-12-28", "completado", 26000),
        (4, 2, "2025-09-01", "2025-09-22", "en_proceso", 37500),
        (5, 4, "2025-11-05", "2025-11-12", "completado", 78200),
        (6, 4, "2025-08-21", "2025-09-20", "pendiente", 800),
        (7, 9, "2025-12-20", "2026-01-19", "en_proceso", 12000),
        (8, 10, "2025-10-15", "2025-10-30", "pendiente", 53700),
        (9, 1, "2026-01-08", "2026-01-31", "completado", 61900),
        (10, 9, "2026-01-06", "2026-01-18", "cancelado", 159000),
        (11, 4, "2025-11-01", "2025-11-24", "completado", 19000),
        (12, 12, "2025-12-26", "2026-01-05", "pendiente", 20000),
        (13, 11, "2025-09-19", "2025-10-16", "en_proceso", 294000),
        (14, 12, "2026-01-28", "2026-02-13", "completado", 47500),
        (15, 9, "2025-08-18", "2025-09-14", "en_proceso", 50800),
        (16, 7, "2025-08-12", "2025-09-04", "cancelado", 183500),
        (17, 4, "2026-01-17", "2026-02-12", "cancelado", 76000),
        (18, 8, "2025-09-28", "2025-10-11", "cancelado", 168000),
        (19, 10, "2026-02-14", "2026-02-25", "en_proceso", 96000),
        (20, 5, "2025-10-14", "2025-11-01", "completado", 71000),
        # ... añade todos los que están en tu archivo si los necesitas
    ]
    cursor.executemany("""
        INSERT INTO pedidos (id_pedido, id_cliente, fecha_anticipo, fecha_entrega, estado, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, pedidos)

    # --- detalle_pedido --- (extracto, igual puedes completar todo el listado) [file:1]
    detalle_pedido = [
        (1, 1, 10, 16, 8000, 128000),
        (2, 1, 4, 16, 2000, 32000),
        (3, 1, 7, 7, 2500, 17500),
        (4, 1, 2, 4, 5000, 20000),
        (5, 1, 7, 12, 2500, 30000),
        (6, 2, 7, 15, 2500, 37500),
        (7, 2, 1, 4, 1000, 4000),
        (8, 2, 1, 13, 1000, 13000),
        (9, 2, 6, 4, 500, 2000),
        (10, 3, 4, 7, 2000, 14000),
        (11, 3, 9, 15, 800, 12000),
        # ... sigue copiando las filas que necesites desde el archivo
    ]
    cursor.executemany("""
        INSERT INTO detalle_pedido (id_detalle, id_pedido, id_insumo, cantidad, precio_unitario, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, detalle_pedido)

    # --- gastos --- (no vienen en el archivo, ejemplo mínimo) [file:1]
    gastos = [
        ("Arriendo taller", "fijo", 1200000, "2026-02-01", "Propietario local", "transferencia"),
        ("Hilo y agujas", "insumo", 85000, "2026-02-10", "Proveedor insumos", "efectivo"),
    ]
    cursor.executemany("""
        INSERT INTO gastos (descripcion, categoria, monto, fecha, pagado_a, medio_pago)
        VALUES (?, ?, ?, ?, ?, ?)
    """, gastos)

    # --- facturas --- (no vienen en el archivo, ejemplo mínimo asociado a pedidos existentes) [file:1]
    facturas = [
        (1, "anticipo", 30000, "2025-11-27", "2025-11-27", "transferencia", "Cuenta A", "Arturo", "pagado"),
        (1, "saldo", 26500, "2025-12-16", None, "efectivo", "Caja", "Arturo", "pendiente"),
        (3, "anticipo", 13000, "2025-12-16", "2025-12-16", "nequi", "Cuenta B", "Arturo", "pagado"),
    ]
    cursor.executemany("""
        INSERT INTO facturas (id_pedido, tipo, monto, fecha_programada, fecha_pago,
                              medio_pago, cuenta_receptora, pagado_por, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, facturas)

    conn.commit()
    conn.close()


# def backup_db(drive, folder_id):
#     conn = sqlite3.connect(DB_PATH)
#     conn.commit()
#     conn.close()

#     file_list = drive.ListFile(
#         {'q': f"'{folder_id}' in parents and title='database.db' and trashed=false"}
#     ).GetList()

#     if file_list:
#         file = file_list[0]
#     else:
#         file = drive.CreateFile({
#             'title': 'database.db',
#             'parents': [{'id': folder_id}]
#         })

#     file.SetContentFile(DB_PATH)
#     file.Upload()
#     print("Base de datos subida a Drive.")


# def load_db(drive, folder_id):
#     file_list = drive.ListFile(
#         {'q': f"'{folder_id}' in parents and title='database.db' and trashed=false"}
#     ).GetList()

#     if file_list:
#         file = file_list[0]
#         file.GetContentFile(DB_PATH)
#         print("Base de datos descargada desde Drive.")
#     else:
#         print("No existe DB en Drive. Creando nueva base...")
#         init_db()
#         backup_db(drive, folder_id)

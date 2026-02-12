import sqlite3

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
        costo_unitario REAL NOT NULL,
        stock_actual REAL DEFAULT 0,
        fecha_actualizacion DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        fecha_pedido DATE DEFAULT CURRENT_DATE,
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
        fecha DATE DEFAULT CURRENT_DATE
    );
    """)

    conn.commit()
    conn.close()

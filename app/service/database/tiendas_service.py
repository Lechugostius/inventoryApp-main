from .database import get_connection

def get_all_tiendas():
    """Obtiene todas las tiendas con información del país."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.id_tienda,
                    t.siglas, 
                    t.nombre_tienda,
                    t.direccion,
                    t.correo,
                    t.id_pais,
                    p.nombre as pais_nombre,
                    p.codigo as pais_codigo
                FROM dbo.Tiendas t
                INNER JOIN dbo.Paises p ON t.id_pais = p.id_pais
                ORDER BY p.nombre, t.siglas
            """)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def get_tiendas_by_pais(pais_id: int):
    """Obtiene tiendas filtradas por país."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.id_tienda,
                    t.siglas, 
                    t.nombre_tienda,
                    t.direccion,
                    t.correo,
                    t.id_pais,
                    p.nombre as pais_nombre,
                    p.codigo as pais_codigo
                FROM dbo.Tiendas t
                INNER JOIN dbo.Paises p ON t.id_pais = p.id_pais
                WHERE t.id_pais = ?
                ORDER BY t.siglas
            """, (pais_id,))
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def get_tienda_by_id(tienda_id: str):
    """Obtiene una tienda específica por su ID."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.id_tienda,
                    t.siglas, 
                    t.nombre_tienda,
                    t.direccion,
                    t.correo,
                    t.id_pais,
                    p.nombre as pais_nombre,
                    p.codigo as pais_codigo
                FROM dbo.Tiendas t
                INNER JOIN dbo.Paises p ON t.id_pais = p.id_pais
                WHERE t.id_tienda = ?
            """, (tienda_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def get_oficinas_centrales():
    """Obtiene las oficinas centrales (CDA en CR y MetroMall en Panamá)."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.id_tienda,
                    t.siglas, 
                    t.nombre_tienda,
                    t.direccion,
                    t.correo,
                    t.id_pais,
                    p.nombre as pais_nombre,
                    p.codigo as pais_codigo
                FROM dbo.Tiendas t
                INNER JOIN dbo.Paises p ON t.id_pais = p.id_pais
                WHERE t.id_tienda IN ('00', 'PTY01')
                ORDER BY t.id_pais
            """)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e
import pyodbc
from config import DB_CONFIG

def get_connection():
    connection_string = f"DRIVER={{{DB_CONFIG['driver']}}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
    return pyodbc.connect(connection_string)

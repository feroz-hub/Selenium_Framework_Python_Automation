import pyodbc
from omsd_automation.utils.config_reader import Config

class DBUtils:
    @staticmethod
    def get_confirmation_code(user_id):
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={Config.get('db.server')};"
            f"DATABASE={Config.get('db.name')};"
            f"UID={Config.get('db.username')};"
            f"PWD={Config.get('db.password')};"
            f"Encrypt=yes;TrustServerCertificate=no;"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 1 ConfirmationCode 
            FROM ConfirmationTable 
            WHERE UserId=? 
            ORDER BY CreatedAt DESC
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

import time
import pyodbc
from omsd_automation.utils.config_reader import Config


class DBUtils:
    @staticmethod
    def get_confirmation_code(serial_number, product_id, retries=5, delay=3):
        """
        Fetch the ConfirmationCode for a given SerialNumber and ProductId with retry mechanism.

        Args:
            serial_number (str): The device serial number.
            product_id (int): The product ID.
            retries (int): Number of retry attempts.
            delay (int): Seconds to wait between retries.

        Returns:
            str | None: ConfirmationCode if found, otherwise None.
        """
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={Config.get('db.server')};"
            f"DATABASE={Config.get('db.name')};"
            f"UID={Config.get('db.username')};"
            f"PWD={Config.get('db.password')};"
            f"Encrypt=yes;TrustServerCertificate=no;"
        )
        cursor = conn.cursor()

        for attempt in range(1, retries + 1):
            cursor.execute("""
                SELECT TOP 1 ConfirmationCode 
                FROM Device
                WHERE SerialNumber = ? AND ProductId = ?
                ORDER BY CreatedAt DESC
            """, (serial_number, product_id))

            row = cursor.fetchone()
            if row and row[0]:
                conn.close()
                return row[0]

            if attempt < retries:
                print(f"[Retry {attempt}/{retries}] ConfirmationCode not found yet. Retrying in {delay}s...")
                time.sleep(delay)

        conn.close()
        return None

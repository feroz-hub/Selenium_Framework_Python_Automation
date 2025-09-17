import time

import pyodbc


class DBUtils:
    @staticmethod
    def get_confirmation_and_unlock(serial_number, product_id, retries=5, delay=3):
        """
        Fetch ConfirmationCode and UnlockCode for a given SerialNumber and ProductId.

        Args:
            serial_number (str): Device serial number
            product_id (int): Product ID
            retries (int): Number of retry attempts
            delay (int): Delay between retries in seconds

        Returns:
            tuple[str | None, str | None]: (ConfirmationCode, UnlockCode)
        """
        server = "omsd-sqlsv-stg3.database.windows.net,1433"
        database = "omsd-sqlsv-stg3"
        username = "omsdSqlAdmin@omsd-sqlsv-stg3"
        password = "8w$Tm%-7ucNxE"

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        cursor = conn.cursor()

        for attempt in range(1, retries + 1):
            cursor.execute("""
                SELECT TOP 1 ConfirmationCode, UnlockCode
                FROM Device
                WHERE SerialNumber = ? AND ProductId = ?
            """, (serial_number, product_id))

            row = cursor.fetchone()
            if row and row[0]:
                conn.close()
                return row[0], row[1]  # (confirmation, unlock)

            if attempt < retries:
                print(f"[Retry {attempt}/{retries}] Codes not ready. Retrying in {delay}s...")
                time.sleep(delay)

        conn.close()
        return None, None


if __name__ == "__main__":
    serial_number = "OSTETEST123456"
    product_id = 1  # replace with a valid test ProductId

    confirm_code = DBUtils.get_confirmation_and_unlock(serial_number, product_id)
    #unlock_code = DBUtils.get_unlock_code(serial_number, product_id)

    if confirm_code:
        print(f"✅ Confirmation code retrieved: {confirm_code}")
    else:
        print("❌ No confirmation code found for the given SerialNumber and ProductId")

    # if unlock_code:
    #     print(f"✅ Unlock code retrieved: {unlock_code}")
    # else:
    #     print("❌ No unlock code found for the given SerialNumber and ProductId")

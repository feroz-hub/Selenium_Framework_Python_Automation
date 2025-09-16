# Assuming DBUtils is already defined and imported
from omsd_automation.utils.db_utils import DBUtils

serial_number = "ABC123456789"  # Replace with actual serial number
product_id = 101                # Replace with actual product ID

confirmation_code = DBUtils.get_confirmation_code(serial_number, product_id)

if confirmation_code:
    print(f"Confirmation Code: {confirmation_code}")
else:
    print("Confirmation Code not found.")

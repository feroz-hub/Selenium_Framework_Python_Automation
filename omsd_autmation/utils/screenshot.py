
import os
from datetime import datetime

def take_screenshot(driver, step_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{step_name}.png")
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")
# utils/data_loader.py
import csv

def load_csv(file_path):
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        return [(row["username"], row["password"], row["expected"]) for row in reader]

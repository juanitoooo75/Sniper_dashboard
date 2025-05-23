import csv
import os

EXPORT_FILE = "trades_export.csv"

def export_trade(trade_data):
    file_exists = os.path.isfile(EXPORT_FILE)
    with open(EXPORT_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=trade_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade_data)

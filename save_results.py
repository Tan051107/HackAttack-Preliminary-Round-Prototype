import json
import csv
import os

def save_as_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_as_csv(data_list, output_path):
    if not data_list:
        return
    keys = data_list[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
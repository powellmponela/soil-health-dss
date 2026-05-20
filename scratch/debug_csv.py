import csv
import json
import os

csv_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unesco_thesaurus\voc001.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print(f"Header: {reader.fieldnames}")
    for row in reader:
        print(f"First row keys: {list(row.keys())}")
        break

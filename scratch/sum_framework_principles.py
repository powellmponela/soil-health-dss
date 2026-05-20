import csv
from collections import defaultdict

file_path = r"c:\SOIL HEALTH\principles_indicators\framework_principle_matrix.csv"

sums = defaultdict(float)

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for key, value in row.items():
            if key.startswith('P_'):
                try:
                    sums[key] += float(value)
                except ValueError:
                    pass

print("Summary of indicators extracted per principle across 64 frameworks:")
for key, total in sorted(sums.items(), key=lambda x: x[1], reverse=True):
    principle = key.replace('P_', '')
    print(f"{principle}: {int(total)}")

import os
import json

fw_dir = "c:/SOIL HEALTH/Frameworks"
json_path = "c:/SOIL HEALTH/data/framework_metadata.json"

with open(json_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

json_filenames = {item.get('filename') for item in metadata if item.get('filename')}
folder_filenames = {f for f in os.listdir(fw_dir) if f.endswith('.pdf')}

print(f"Files in folder: {len(folder_filenames)}")
print(f"Files in JSON: {len(json_filenames)}")

missing_in_json = folder_filenames - json_filenames
missing_in_folder = json_filenames - folder_filenames

print(f"\nMissing in JSON (present in folder):")
for f in missing_in_json:
    print(f"  - {f}")

print(f"\nMissing in folder (present in JSON):")
for f in missing_in_folder:
    print(f"  - {f}")

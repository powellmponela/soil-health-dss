import extract_msg
import pandas as pd
import os

def extract_logic(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    msg = extract_msg.Message(file_path)
    print(f"Parsing: {msg.subject}")
    
    # Extract body content for logic rules regarding the 13 principles
    with open("logic_reference.txt", "w", encoding='utf-8') as f:
        f.write(msg.body)
    
    # If matrix data is attached as CSV/Excel within the .msg
    for attachment in msg.attachments:
        filename = attachment.shortFilename or attachment.longFilename
        attachment.save(customPath=".")
        print(f"Saved attachment: {filename}")

if __name__ == "__main__":
    # Ensure the script runs even if the file isn't present yet
    target_file = "Fw Soil Health Framework- decision support system.msg"
    if os.path.exists(target_file):
        extract_logic(target_file)
    else:
        print(f"Please place '{target_file}' in the scripts directory.")

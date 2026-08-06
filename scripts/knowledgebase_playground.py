import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Automatically finds .env file
openwebui_api_key = os.getenv('OPENWEBUI_API_KEY')


BASE_URL = "http://localhost:3000/api/v1"
API_KEY = openwebui_api_key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def upload_file(file_path):
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/files/", headers=HEADERS, files={"file": f})
    if res.status_code == 200:
        return res.json()["id"]
    print(f"Failed to upload {file_path}: {res.text}")
    return None

def create_knowledge_base(name, description, file_ids):
    json_headers = {**HEADERS, "Content-Type": "application/json"}
    payload = {
        "name": name,
        "description": description,
        "data": {"file_ids": file_ids}
    }
    res = requests.post(f"{BASE_URL}/knowledge/create", headers=json_headers, json=payload)
    if res.status_code == 200:
        print(f"\nKnowledge Base '{name}' created! ID: {res.json()['id']}")
    else:
        print(f"\nFailed to create Knowledge Base: {res.text}")

# Folder containing docs to index
folder_path = "./"
file_name = "2026_soluciones.pdf"
file_ids = []

# for file_name in os.listdir(folder_path):
#     full_path = os.path.join(folder_path, file_name)
#     if os.path.isfile(full_path):
#         fid = upload_file(full_path)
#         if fid:
#             file_ids.append(fid)

# full_path = os.path.join(folder_path, file_name)
# print(full_path)
fid = upload_file(file_name)
if fid:
    print(fid)
    file_ids.append(fid)

if file_ids:
    create_knowledge_base(
        name="Project Documentation",
        description="Auto-indexed folder of technical specs",
        file_ids=file_ids
    )
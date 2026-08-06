import os
import requests
from dotenv import load_dotenv
import time


load_dotenv()  # Automatically finds .env file
openwebui_api_key = os.getenv('OPENWEBUI_API_KEY')


BASE_URL = "http://localhost:3000/api/v1"
API_KEY = openwebui_api_key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def upload_file(token, file_path):
    url = 'http://localhost:3000/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()


def wait_for_file_processing(token, file_id, timeout=300, poll_interval=2):
    """
    Wait for a file to finish processing.
    
    Returns:
        dict: Final status with 'status' key ('completed' or 'failed')
    
    Raises:
        TimeoutError: If processing doesn't complete within timeout
    """
    url = f'http://localhost:3000/api/v1/files/{file_id}/process/status'
    headers = {'Authorization': f'Bearer {token}'}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        result = response.json()
        status = result.get('status')
        
        if status == 'completed':
            return result
        elif status == 'failed':
            raise Exception(f"File processing failed: {result.get('error')}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"File processing did not complete within {timeout} seconds")


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


def add_file_to_knowledge(token, knowledge_id, file_id):
    url = f'http://localhost:3000/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Folder containing docs to index
folder_path = os.path.expanduser("~/Downloads/f2/")
file_name = "TD-actividad-01-ciclos.pdf"
file_ids = []

# for file_name in os.listdir(folder_path):
#     full_path = os.path.join(folder_path, file_name)
#     if os.path.isfile(full_path):
#         fid = upload_file(full_path)
#         if fid:
#             file_ids.append(fid)

full_path = os.path.join(folder_path, file_name)
print(full_path)
fid = upload_file(full_path)
if fid:
    print(fid)
    file_ids.append(fid)

if file_ids:
    create_knowledge_base(
        name="Project Documentation",
        description="Auto-indexed folder of technical specs",
        file_ids=file_ids
    )
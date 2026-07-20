import requests
from utils.config import (
    UPLOAD_ENDPOINT,
    FILES_ENDPOINT,
    DOWNLOAD_ENDPOINT,
    DELETE_ENDPOINT,
    SHARE_ENDPOINT
)


def get_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


# ----------------------------
# List Files
# ----------------------------
def list_files(access_token):

    response = requests.get(
        FILES_ENDPOINT,
        headers=get_headers(access_token)
    )

    if response.status_code == 200:
        return response.json()

    return []


# ----------------------------
# Generate Upload URL
# ----------------------------
def generate_upload_url(access_token, filename):

    body = {
        "fileName": filename
    }

    response = requests.post(
        UPLOAD_ENDPOINT,
        headers=get_headers(access_token),
        json=body
    )

    if response.status_code == 200:
        return response.json()

    return None


# ----------------------------
# Download File
# ----------------------------
def download_file(access_token, file_id):

    response = requests.get(
        f"{DOWNLOAD_ENDPOINT}?fileId={file_id}",
        headers=get_headers(access_token)
    )

    if response.status_code == 200:
        return response.json()

    return None


# ----------------------------
# Delete File
# ----------------------------
def delete_file(access_token, file_id):

    body = {
        "fileId": file_id
    }

    response = requests.delete(
        DELETE_ENDPOINT,
        headers=get_headers(access_token),
        json=body
    )

    return response.status_code == 200


# ----------------------------
# Share File
# ----------------------------
def share_file(access_token, file_id, expires=3600):

    body = {
        "fileId": file_id,
        "expiresIn": expires
    }

    response = requests.post(
        SHARE_ENDPOINT,
        headers=get_headers(access_token),
        json=body
    )

    if response.status_code == 200:
        return response.json()

    return None

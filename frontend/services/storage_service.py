"""
All API Gateway / Lambda communication for file operations.
"""

import requests

from core.config import (
    UPLOAD_ENDPOINT,
    FILES_ENDPOINT,
    DOWNLOAD_ENDPOINT,
    DELETE_ENDPOINT,
    SHARE_ENDPOINT,
    DEFAULT_SHARE_EXPIRY_SECONDS,
)
from core.session import get_access_token


def _headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }


def list_files():
    try:
        response = requests.get(FILES_ENDPOINT, headers=_headers())
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("message", "Failed to fetch files")
    except Exception as e:
        return False, str(e)


def upload_file(file_name: str, file_bytes: bytes):
    try:
        response = requests.post(
            UPLOAD_ENDPOINT, headers=_headers(), json={"filename": file_name}
        )
        if response.status_code != 200:
            return False, response.json().get("message", "Failed to get upload URL")

        upload_url = response.json()["uploadURL"]
        put_response = requests.put(upload_url, data=file_bytes)

        if put_response.status_code == 200:
            return True, "File uploaded successfully"
        return False, f"S3 upload failed with status {put_response.status_code}"

    except Exception as e:
        return False, str(e)


def download_file(file_id: str):
    try:
        response = requests.get(
            DOWNLOAD_ENDPOINT, headers=_headers(), params={"fileId": file_id}
        )
        if response.status_code == 200:
            return True, response.json()["downloadURL"]
        return False, response.json().get("message", "Failed to get download URL")
    except Exception as e:
        return False, str(e)


def delete_file(file_id: str):
    try:
        response = requests.delete(
            DELETE_ENDPOINT, headers=_headers(), json={"fileId": file_id}
        )
        if response.status_code == 200:
            return True, response.json().get("message", "File deleted successfully")
        return False, response.json().get("message", "Failed to delete file")
    except Exception as e:
        return False, str(e)


def share_file(file_id: str, expires_in: int = DEFAULT_SHARE_EXPIRY_SECONDS):
    try:
        response = requests.post(
            SHARE_ENDPOINT,
            headers=_headers(),
            json={"fileId": file_id, "expiresIn": expires_in},
        )
        if response.status_code == 200:
            return True, response.json()["shareURL"]
        return False, response.json().get("message", "Failed to generate share link")
    except Exception as e:
        return False, str(e)

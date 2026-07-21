"""
Central configuration — all AWS/API identifiers live here only.
"""

# ===================== AWS / COGNITO =====================
AWS_REGION = "ap-south-1"

USER_POOL_ID = "ap-south-1_8FC3UiBc2"
APP_CLIENT_ID = "32pgkcil5nrrvjr71jhth0mojj"

# Set only if your App Client has a Client Secret enabled.
APP_CLIENT_SECRET = None

S3_BUCKET = "mini-dropbox-storage"

# ===================== API GATEWAY =====================
API_BASE_URL = "https://8gc8p2admi.execute-api.ap-south-1.amazonaws.com"

UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"
FILES_ENDPOINT = f"{API_BASE_URL}/files"
DOWNLOAD_ENDPOINT = f"{API_BASE_URL}/download"
DELETE_ENDPOINT = f"{API_BASE_URL}/file"
SHARE_ENDPOINT = f"{API_BASE_URL}/share"

# ===================== APP =====================
APP_TITLE = "Mini Dropbox"
APP_ICON = "📦"
DEFAULT_SHARE_EXPIRY_SECONDS = 3600

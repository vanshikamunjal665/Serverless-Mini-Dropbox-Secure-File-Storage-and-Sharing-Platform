"""
All Cognito interactions: login, sign up, confirm account.
"""

import boto3
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError

from core.config import AWS_REGION, APP_CLIENT_ID, APP_CLIENT_SECRET

import streamlit as st

def _get_cognito_client():
    if "AWS_ACCESS_KEY_ID" in st.secrets:
        return boto3.client(
            "cognito-idp",
            region_name=AWS_REGION,
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        )
    return boto3.client("cognito-idp", region_name=AWS_REGION)

_client = _get_cognito_client()


def _secret_hash(username: str) -> str:
    message = username + APP_CLIENT_ID
    digest = hmac.new(
        APP_CLIENT_SECRET.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def login(username: str, password: str):
    try:
        auth_params = {"USERNAME": username, "PASSWORD": password}
        if APP_CLIENT_SECRET:
            auth_params["SECRET_HASH"] = _secret_hash(username)

        response = _client.initiate_auth(
            ClientId=APP_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=auth_params,
        )
        result = response["AuthenticationResult"]

        return True, {
            "access_token": result["AccessToken"],
            "id_token": result["IdToken"],
            "refresh_token": result.get("RefreshToken"),
        }

    except ClientError as e:
        return False, {"message": e.response["Error"]["Message"]}
    except Exception as e:
        return False, {"message": str(e)}


def sign_up(username: str, password: str, email: str):
    try:
        params = {
            "ClientId": APP_CLIENT_ID,
            "Username": username,
            "Password": password,
            "UserAttributes": [{"Name": "email", "Value": email}],
        }
        if APP_CLIENT_SECRET:
            params["SecretHash"] = _secret_hash(username)

        _client.sign_up(**params)
        return True, {"message": "Account created. Check your email for the verification code."}

    except ClientError as e:
        return False, {"message": e.response["Error"]["Message"]}
    except Exception as e:
        return False, {"message": str(e)}


def confirm_sign_up(username: str, code: str):
    try:
        params = {
            "ClientId": APP_CLIENT_ID,
            "Username": username,
            "ConfirmationCode": code,
        }
        if APP_CLIENT_SECRET:
            params["SecretHash"] = _secret_hash(username)

        _client.confirm_sign_up(**params)
        return True, {"message": "Account verified. You can log in now."}

    except ClientError as e:
        return False, {"message": e.response["Error"]["Message"]}
    except Exception as e:
        return False, {"message": str(e)}

import boto3
from botocore.exceptions import ClientError
from utils.config import REGION, CLIENT_ID

client = boto3.client(
    "cognito-idp",
    region_name=REGION
)

def login(email, password):
    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password
            }
        )

        return {
            "success": True,
            "access_token": response["AuthenticationResult"]["AccessToken"],
            "id_token": response["AuthenticationResult"]["IdToken"]
        }

    except ClientError as e:
        return {
            "success": False,
            "message": e.response["Error"]["Message"]
        }

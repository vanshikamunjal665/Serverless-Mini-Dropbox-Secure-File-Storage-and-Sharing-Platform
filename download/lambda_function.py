import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

TABLE_NAME = os.environ["TABLE_NAME"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    try:

        # Get authenticated user
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = claims["sub"]

        # Get FileID from query string
        file_id = event["queryStringParameters"]["fileId"]

        # Fetch metadata
        response = table.get_item(
            Key={
                "UserID": user_id,
                "FileID": file_id
            }
        )

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "File not found"
                })
            }

        file_key = response["Item"]["FileKey"]

        # Generate download URL
        download_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "downloadURL": download_url
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }

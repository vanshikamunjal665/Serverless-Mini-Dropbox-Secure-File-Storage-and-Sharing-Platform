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

        # Read request body
        body = json.loads(event["body"])

        file_id = body["fileId"]
        expires_in = body.get("expiresIn", 3600)

        # Get file metadata
        response = table.get_item(
            Key={
                "UserID": user_id,
                "FileID": file_id
            }
        )

        # File not found
        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "File not found"
                })
            }

        item = response["Item"]

        file_key = item["FileKey"]

        # Generate share URL
        share_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key
            },
            ExpiresIn=expires_in
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "shareURL": share_url,
                "expiresIn": expires_in
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }

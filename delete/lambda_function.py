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

        body = json.loads(event["body"])
        file_id = body["fileId"]

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

        # Delete file from S3
        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=file_key
        )

        # Delete metadata from DynamoDB
        table.delete_item(
            Key={
                "UserID": user_id,
                "FileID": file_id
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File deleted successfully"
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }

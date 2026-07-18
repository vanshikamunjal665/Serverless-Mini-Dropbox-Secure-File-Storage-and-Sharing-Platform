import json
import boto3
import os

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    try:

        body = json.loads(event["body"])

        user_id = body["userId"]
        file_id = body["fileId"]
        file_key = body["fileKey"]

        # Delete from S3
        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=file_key
        )

        # Delete metadata
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

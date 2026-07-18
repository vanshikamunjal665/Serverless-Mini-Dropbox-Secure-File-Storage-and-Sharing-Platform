import json
import boto3
import os

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):

    try:

        file_key = event["queryStringParameters"]["fileKey"]

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

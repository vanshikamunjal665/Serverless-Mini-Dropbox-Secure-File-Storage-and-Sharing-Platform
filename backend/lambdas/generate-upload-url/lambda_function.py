import json
import boto3
import uuid
import os

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):

    try:
        # Get authenticated user's JWT claims
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = claims["sub"]

        # Read filename from request body
        body = json.loads(event["body"])
        filename = body["filename"]

        # Store files inside the user's folder
        file_key = f"uploads/{user_id}/{uuid.uuid4()}_{filename}"

        # Generate pre-signed upload URL
        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
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
                "uploadURL": upload_url,
                "fileKey": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": str(e)
            })
        }

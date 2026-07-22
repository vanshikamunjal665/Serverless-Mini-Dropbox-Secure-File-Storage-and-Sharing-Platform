import json
import boto3
import uuid
from urllib.parse import unquote_plus
from datetime import datetime
import os

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    try:

        for record in event["Records"]:

            bucket = record["s3"]["bucket"]["name"]
            object_key = unquote_plus(record["s3"]["object"]["key"])
            file_size = record["s3"]["object"]["size"]          # <-- NEW

            parts = object_key.split("/")
            user_id = parts[1]
            file_name = parts[-1]

            file_id = str(uuid.uuid4())
            upload_time = datetime.utcnow().isoformat()

            table.put_item(
                Item={
                    "UserID": user_id,
                    "FileID": file_id,
                    "Bucket": bucket,
                    "FileName": file_name,
                    "FileKey": object_key,
                    "UploadTime": upload_time,
                    "FileSize": file_size                        # <-- NEW
                }
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Metadata stored successfully"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }

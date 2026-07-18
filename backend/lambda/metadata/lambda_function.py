import json
import boto3
import os
import uuid
from datetime import datetime
from urllib.parse import unquote_plus

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    try:

        for record in event["Records"]:

            bucket = record["s3"]["bucket"]["name"]

            file_key = unquote_plus(record["s3"]["object"]["key"])

            file_name = file_key.split("/")[-1]

            # Temporary user until Cognito integration
            user_id = "demo-user"

            file_id = str(uuid.uuid4())

            table.put_item(
                Item={
                    "UserID": user_id,
                    "FileID": file_id,
                    "Bucket": bucket,
                    "FileName": file_name,
                    "FileKey": file_key,
                    "UploadTime": datetime.utcnow().isoformat()
                }
            )

        return {
            "statusCode": 200,
            "body": json.dumps("Metadata stored successfully")
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }

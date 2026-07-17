import json
import boto3
import os
import uuid

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]

ALLOWED_EXTENSIONS = {
    "pdf",
    "jpg",
    "jpeg",
    "png",
    "doc",
    "docx",
    "txt"
}


def lambda_handler(event, context):

    try:

        body = json.loads(event["body"])

        filename = body.get("filename")

        if not filename:
            return {
                "statusCode":400,
                "body":json.dumps({
                    "message":"Filename is required"
                })
            }

        extension = filename.split(".")[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            return {
                "statusCode":400,
                "body":json.dumps({
                    "message":"Unsupported file type"
                })
            }

        file_id = str(uuid.uuid4())

        object_key = f"uploads/{file_id}_{filename}"

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket":BUCKET_NAME,
                "Key":object_key
            },
            ExpiresIn=300
        )

        return {

            "statusCode":200,

            "headers":{
                "Content-Type":"application/json"
            },

            "body":json.dumps({

                "uploadURL":upload_url,

                "fileKey":object_key

            })
        }

    except Exception as e:

        return{

            "statusCode":500,

            "body":json.dumps({

                "message":str(e)

            })
        }

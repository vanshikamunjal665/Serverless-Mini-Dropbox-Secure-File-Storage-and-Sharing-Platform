import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    try:

        # Temporary until Cognito integration
        user_id = "demo-user"

        response = table.query(
            KeyConditionExpression=Key("UserID").eq(user_id)
        )

        files = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(files)
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }

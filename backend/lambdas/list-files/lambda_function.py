import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    """Converts DynamoDB's Decimal type into int/float so json.dumps works."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):

    try:
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = claims["sub"]

        response = table.query(
            KeyConditionExpression=Key("UserID").eq(user_id)
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response["Items"], cls=DecimalEncoder)   # <-- only change
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }

from decimal import Decimal
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
from flask import Flask, render_template, request
import key_config as keys

app = Flask(__name__)


@app.route('/Remove')
def Remove(title, year, artist, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:5000")

    table = dynamodb.Table('subscription')

    try:
        response = table.delete_item(
            Key={
                'title': title,
                'artist': artist,
                'year': year
            },
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response

import boto3
# Get the service resource.
import key_config as keys

dynamodb = boto3.resource('dynamodb')

table = dynamodb.create_table(
    TableName='subscription',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'title',
            'KeyType': 'RANGE'
        }

    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10,
    }
)

# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='Subscription')



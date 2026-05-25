# Python Lambda function to fetch account details and name from DynamoDB
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('account')  # Replace 'YourTableName' with your actual DynamoDB table name

def get_account_details(event, context):
    # Assuming you have the username in the 'username' field of the event
    username = event['queryStringParameters']['username']

    # Retrieve the item from DynamoDB based on the username
    response = table.get_item(Key={'username': username})

    if 'Item' in response:
        item = response['Item']
        account_details = item.get('account_details', 'N/A')
        name = item.get('name', 'N/A')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'account_details': account_details,
                'name': name
            })
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'User not found'})
        }



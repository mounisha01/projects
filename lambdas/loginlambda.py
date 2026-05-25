# login_lambda.py
import boto3
import json

def lambda_handler(event, context):
    try:
        # Assuming you have a DynamoDB table named 'Users'
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')

        # Retrieve username and password from the event
        username = event['username']
        password = event['password']

        # Query the DynamoDB table to check if the user exists and the password is correct
        response = table.get_item(Key={'username': username})

        if 'Item' in response:
            user_data = response['Item']
            if user_data['password'] == password:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Login successful!'})
                }
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Invalid credentials'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error'})
        }

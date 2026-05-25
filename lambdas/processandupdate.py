import boto3
import re
import json

def extract_text_from_image(image_bucket, image_filename):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=image_bucket, Key=image_filename)
    image_content = response['Body'].read()

    textract = boto3.client('textract')
    response = textract.detect_document_text(Document={'Bytes': image_content})
    extracted_text = '\n'.join([item.get('Text','') for item in response['Blocks'] if item['BlockType'] == 'WORD'])
    return extracted_text

def process_extracted_text(extracted_text):
    amount_pattern = r'\*\*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\*\*'
    name_pattern = r'\*\*([^\*]+)'

    amount_match = re.search(amount_pattern, extracted_text)
    extracted_amount = amount_match.group(1).replace(',', '') if amount_match else None

    name_match = re.search(name_pattern, extracted_text)
    Nameonthecheque = name_match.group(1).replace(' ', '\n') if name_match else None

    return extracted_amount, Nameonthecheque

def update_user_account(username, extracted_amount):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('account')
    
    response = table.get_item(Key={'username': username})
    balance = response.get('Item', {})

    # Update the account balance based on the extracted amount
    balance['amount'] = str(int(balance.get('amount', 0)) + int(float(extracted_amount)))

    # Save the updated account information back to DynamoDB
    table.put_item(Item=balance)

def lambda_handler(event, context):
    # Assuming the event contains the S3 bucket and filename for the uploaded image
    print(len(event['Records']))
    image_bucket = event['Records'][0]['s3']['bucket']['name']
    image_filename = event['Records'][0]['s3']['object']['key']
    # print(bucket_name,s3_key)

    # Extract text from the image using Textract
    extracted_text = extract_text_from_image(image_bucket, image_filename)

    # Process the extracted text to get the amount and user name
    extracted_amount, name = process_extracted_text(extracted_text)

    # Assuming you have the username in the 'username' field of the event
    username = "admin"

    # Update the user's account with the extracted amount
    update_user_account(username, extracted_amount)

    # Send an SNS notification to the user about the account update
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:752190563141:cloudproject'
    message = f"Dear {name}, your account has been updated with {extracted_amount}."
    sns.publish(TopicArn=topic_arn, Message=message)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Cheque processed successfully.",
            "account_details": extracted_amount,
            "name": name
        })
    }

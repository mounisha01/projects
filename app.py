from flask import Flask, render_template,request, redirect, session,json,jsonify
import requests
import boto3
import ast
from botocore.exceptions import ClientError
import re,os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
load_dotenv()
app = Flask(__name__)
api_gateway_url = os.environ.get('API_GATEWAY_URL')
access_key = 'ASIAYYRV2BGBQIVQYB5T'
secret_key='j5lRV8Bv1WR7Z+5ZqF07Cjv/O2NXAGOAatrN3JoX'
app.secret_key = 'kc930D93cRBr1OE7l4TCTvKXphS/GqbdjTYtvnPH' 
session_key = 'FwoGZXIvYXdzEDkaDDyx66ONBOoc9GaRuSLEAQtlLDsCsT7N/TneWY3jQrAoRyQDKkslrLNHOK5tZSlz2kYeTFpaYPbWqdFgigDCX8HoF4r6HvprtcYgUVExBew0tClT19x/rInH+F8mIYdOvvZhLqIblDWe9SEwwe+PPihLzgKXxj/no8XksgorwusjHTHnwvjI92/Me5BT+wUvFzKbno+Od7UAGTQgD1T/RIUW6xfhcSdzTjgvlNEdEw34tJYfMnGaOGG9trurOYhtrTZ7uzuwsw/XOM0CtR7GNlLu1Ago8ZqfpgYyLRfC64ujyKAULMsS03fV0UfY/v8fBsI331Zk/zyyxpGup82jCaKz2o7y5v3OsA=='
s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key,aws_session_token=session_key)
# Initialize S3 client
# dynamodb = boto3.resource('dynamodb')  # Initialize DynamoDB resource
# sns = boto3.client('sns')  # Initialize SNS client

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        payload = {
                "username": username,
                "password": password
            }
        print(payload)

            # Make the API call to the API Gateway
        response = requests.post(f'https://{api_gateway_url}.execute-api.us-east-1.amazonaws.com/dev/login', json=payload)

        # Check the response from the API Gateway
        if response.status_code == 200:
            # If the login is successful, store the username in the session and redirect to the home page
            session['username'] = username
            return redirect('/home')
        else:
            # If the login fails, display an error message on the login page
            return render_template('login.html', error='Invalid credentials')

    # For GET requests or when the login fails, render the login page
    return render_template('login.html')

   

@app.route('/home', methods=['GET','POST'])
def home():
    if request.method=='GET':
    # username = request.args.get('username')
        username = session.get('username')
        lambda_url = f'https://{api_gateway_url}.execute-api.us-east-1.amazonaws.com/dev/home'  # Replace 'your-lambda-function-url' with the actual URL of your Lambda function
        payload = {
                    "username": username,
                    
                }
        # Make a request to the Lambda function
        response = requests.post(lambda_url,json=payload)
        # data=response.text.split(',')
        # data_str = ''.join(data)
        response_json_str = response.text
        print("response",response)
        print("response_json_str",response_json_str)
# Parse the JSON string in the "body" field
        parsed_body = json.loads(response_json_str)

# Extract the account_details and name
        print(parsed_body)
        body_json = json.loads(parsed_body['body'])

# Extract the account_details and name
        account_details = body_json['account_details']
        name = body_json['name']

        print("ndwnvfh",account_details,name)
        # data=response.json()
    return render_template('home.html',account_details=account_details,name=name)
    # accounts=accounts
    # else:
    #     return redirect('/login')
    
@app.route('/edeposit', methods=['GET', 'POST'])

def edeposit():
    
    if request.method == 'POST':
        # Get the uploaded file from the form
        file = request.files['cheque_picture']
        username = session.get('username')
        # Upload the file to S3 bucket
        # Replace 'your-s3-bucket-name' with the actual bucket name
        bucket_name = 'chequesbucket-111'
        file_name = file.filename
        s3.upload_fileobj(file, 'chequesbucket-111', file.filename)
        image_path= "s3://chequesbucket-111/file.filename"
        return redirect('/home')

    return render_template('edeposit.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


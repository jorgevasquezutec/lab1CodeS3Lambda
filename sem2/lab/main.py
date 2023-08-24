import boto3
import json

def lambda_handler(event, context):
    s3 = boto3.resource('s3')

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    obj = s3.Object(bucket, key)
    body = obj.get()['Body'].read().decode('utf-8')
    print(body)

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
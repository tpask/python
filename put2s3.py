#put a json in s3 bucket
import boto3
import json

bucket='pask'

data = {"HelloWorld": []}
s3 = boto3.resource('s3')
obj = s3.Object(bucket,'event.json')
obj.put(Body=json.dumps(data))

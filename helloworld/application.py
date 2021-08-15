#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
from flask_cors import CORS
import boto3

application = Flask(__name__)
CORS(application, resources={r"/": {"origins": ""}})

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)
    
@application.route('/get_cops', methods=['GET'])
def get_id():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('cops')
    # replace table scan ###
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)
    
# curl -i -X POST -d'{"name":"Shiran", "department":"Surgery", "years":"20"}' -H "Content-Type: application/json" http://localhost:5000/set_doctor/4
@application.route('/set_cop/<id>', methods=['POST'])
def set_cop(id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('cops')
    # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    name = data_dict.get('name','default')
    age = data_dict.get('age','defualt')
    phone = data_dict.get('phone', 'default')
    rank = data_dict.get('rank', 'default')

    item={
    'id': id,
    'name': name,
    'age': age, 
    'phone': phone,
    'rank' : rank
     }
    table.put_item(Item=item)
    
    return Response(json.dumps(item), mimetype='application/json', status=200)

if __name__ == '__main__':
    flaskrun(application)

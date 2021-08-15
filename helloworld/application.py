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
    

#curl -i http://"localhost:8000/delete_cops?id=1"
@application.route('/del_cop' , methods=['GET'])

def delete_cop():
    id=request.args.get('id')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('cops')
    
    resp = table.delete_item(
        Key={
            'id':id
        }
        )
    print (str(resp))
    return Response(json.dumps(str(resp)), mimetype='application/json', status=200)
    
    
    
#curl localhost:8000/analyze/my-upload-image/male.jpg  

@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='my-upload-image', image='yarden.jpeg'):
    return detect_labels(bucket, image)
def detect_labels(bucket, key, max_labels=3, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')
    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image
    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])
    


#curl localhost:8000/comp_face/shiran.jpeg/shiran2.jpeg

@application.route('/comp_face/<source_image>/<target_image>', methods=['GET'])
def compare_face(source_image, target_image):
    # change region and bucket accordingly
    region = 'us-east-1'
    bucket_name = 'my-upload-image'
	
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": target_image,
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=50,
    )
    # return 0 if below similarity threshold
    return json.dumps(response['FaceMatches'] if response['FaceMatches'] != [] else [{"Similarity": 0.0}])
    



if __name__ == '__main__':
    flaskrun(application)

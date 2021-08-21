#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
import boto3
from flask_cors import CORS
import datetime
from datetime import datetime
import simplejson as json

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

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
    return Response(json.dumps(resp['Items']), mimetype='application/json', status=200)

# curl -i http://"localhost:8000/set_cop?id=8&name=Dor&age=23&phone=052455&rank=2"
@application.route('/set_cop', methods=['GET'])
def set_doc():
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('cops')
    cid = request.args.get('id')
    name = request.args.get('name')
    age = request.args.get('age')
    phone = request.args.get('phone')
    rank = request.args.get('rank')
    item={
    'id': cid,
    'name': name,
    'age': age, 
    'phone': phone,
    'rank' : rank
     }
    table.put_item(Item=item)
    
    return Response(json.dumps(item), mimetype='application/json', status=200)

#curl -i http://"localhost:5000/del_doctor?id=1"
@application.route('/del_cop' , methods=['GET'])
def del_doc():
    id=request.args.get('id')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('cops')
    
    resp = table.delete_item(
        Key={
            'id':id
        }
        )
    print (str(resp))
    return Response(json.dumps(resp), mimetype='application/json', status=200)

#curl localhost:8000/analyze/doctorspictures/doc1.jpg  

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
    


#curl localhost:8000/comp_face/doc1.jpg/doc2.jpg

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
    
    
@application.route('/upload_image' , methods=['POST'])
def uploadImage():
    mybucket = 'my-upload-image'
    filobject = request.files['img']
    s3 = boto3.resource('s3', region_name='us-east-1')
    date_time = datetime.now()
    dt_string = date_time.strftime("%d-%m-%Y-%H-%M-%S")
    filename = "%s.jpg" % dt_string
    s3.Bucket(mybucket).upload_fileobj(filobject, filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
    imageUrl='https://my-upload-image.s3.amazonaws.com/%s'%filename
    return {"imageUrl": imageUrl}

# @application.route('/upload_image', methods=['GET'])
# def upload_file():
#     time = str(datetime.now())
#     file_name = 'myUpload' + time
#     bucket = 'my-upload-image'
#     client = boto3.client('s3')
#     return client.put_object(Body='', Bucket=bucket, Key=file_name)

if __name__ == '__main__':
    flaskrun(application)
import base64
from flask import request
from flask_restful import Resource
from datetime import datetime
import boto3
from config import Config

class RekognitionResource(Resource) :
    def get(self) :

        # 데이터 받아오기         
        sourceImage = request.files['sourceImage']
        targetImage = request.files['targetImage']

        current_time = datetime.now()
        sourceImage_file_name = 'sourceImage' + current_time.isoformat().replace(':', '_') + '.jpg'
        targetImage_file_name = 'targetImage' + current_time.isoformat().replace(':', '_') + '.jpg'

        sourceImage.filename = sourceImage_file_name
        targetImage_file_name = targetImage_file_name

        # S3 저장
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(sourceImage, Config.S3_BUCKET, sourceImage_file_name,
                                  ExtraArgs= {'ACL' : 'public-read', 'ContentType' : sourceImage.content_type})
            client.upload_fileobj(targetImage, Config.S3_BUCKET, targetImage_file_name,
                                  ExtraArgs= {'ACL' : 'public-read', 'ContentType' : targetImage.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        # 얼굴 비교
        client = boto3.client('rekognition', 'ap-northeast-2', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        response = client.compare_faces(SimilarityThreshold = 50,
                                      SourceImage = {"S3Object" : { "Bucket": Config.S3_BUCKET, "Name": sourceImage_file_name}},
                                      TargetImage = {"S3Object" : { "Bucket": Config.S3_BUCKET, "Name": targetImage_file_name}})
        
        return {'result': 'success', 'Info': response},200

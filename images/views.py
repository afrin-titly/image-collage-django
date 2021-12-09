from rest_framework import fields, status
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from .serializers import UserSerializer, ImageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import boto3
from botocore.exceptions import NoCredentialsError
from decouple import config
from rest_framework_simplejwt.authentication import JWTAuthentication
import io, base64, os
from PIL import Image
from datetime import datetime


#setup environment variable
#https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5#:~:text=To%20set%20and%20get%20environment%20variables%20in%20Python%20you%20can,Get%20environment%20variables%20USER%20%3D%20os.

class UserList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class ImageCollage(APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            user = response[1].payload['user_id']
        else:
            print("No token is provided in the header or the header is missing")

        # user = request.data['user']

        # images = dict((request.data).lists())['image']
        images = request.data["images"]
        flag = 1
        arr = []
        s3 = boto3.client(
            's3',
            region_name = 'ap-northeast-1',
            aws_access_key_id = config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY')
        )
        bucket = 'image-collage'
        # https://stackoverflow.com/questions/52903232/how-to-upload-multiple-images-using-django-rest-framework
        now = datetime.now()

        for image in images:
            try:
                img = image["url"].split("base64,")
                i = Image.open(io.BytesIO(base64.decodebytes(bytes(img[1], "utf-8"))))
                filename = str(user)+"_"+str(now.strftime("%Y%m%d%H%M%S"))+"."+image["extention"]
                i.save("media/"+filename)
                s3.upload_file("media/"+filename, bucket, filename)
                print("Upload Successful")
                data = {'user': user, 'image': filename}
                serializer = ImageSerializer(data=data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    arr.append(serializer.data)
                    os.remove("media/"+filename)
                else:
                    flag = 0
                    print(serializer.is_valid())
            except FileNotFoundError:
                print("File not error.")
            except NoCredentialsError:
                print("Credentials not available.")

        if flag == 1:
            return Response(arr, status=status.HTTP_200_OK)
        else:
            return Response(arr, status=status.HTTP_400_BAD_REQUEST)


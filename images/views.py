from rest_framework import status
from .models import ImageCollageModel
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

s3 = boto3.client(
      's3',
      region_name = 'ap-northeast-1',
      aws_access_key_id = config('AWS_ACCESS_KEY_ID'),
      aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY')
  )
bucket = 'image-collage'

JWT_authenticator = JWTAuthentication()
#setup environment variable
#https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5#:~:text=To%20set%20and%20get%20environment%20variables%20in%20Python%20you%20can,Get%20environment%20variables%20USER%20%3D%20os.

class UserList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class ImageCollage(APIView):
    # permission_classes = (permissions.IsAuthenticated,)


  def post(self, request, format=None):

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
                # TODO: files was not removed
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

  def get(self, request, format=None):
    response = JWT_authenticator.authenticate(request)
    if response is not None:
        user = response[1].payload['user_id']
    else:
        print("No token is provided in the header or the header is missing")

    user_images = ImageCollageModel.objects.all()
    # TODO: loop through user images and show them in front
    print(user_images)
    url = s3.generate_presigned_url('get_object',
        Params={
            'Bucket': bucket,
            'Key': '2_20211213123752.jpg',
        },
        ExpiresIn=86400)

    print(url)
    return Response("comes successfully", status=status.HTTP_200_OK)

# "https://s3-ap-northeast-1.amazonaws.com/image-collage/2_20211213123752.jpg" % (location, bucket_name, key)

from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ImageCollageModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username',)

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCollageModel
        fields = ('user', 'image')
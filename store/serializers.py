from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'face_image_path', 'face_embedding', 'username', 'gender', 'age', 'balance']


class ProductsShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'price', 'image_url', 'gender', 'first_age', 'last_age']


class ProductShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'price', 'image_url', 'gender', 'first_age', 'last_age']
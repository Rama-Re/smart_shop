from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'face_image_path', 'face_embedding', 'username', 'gender', 'age', 'balance']


class ProductsShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'description', 'category', 'price', 'image_url', 'gender', 'first_age', 'last_age']


class ProductShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'price', 'image_url', 'gender', 'first_age', 'last_age']


# ClothesInfo Serializer
class ClothesInfoSerializer(serializers.ModelSerializer):
    length = serializers.SerializerMethodField()
    sleeve_length = serializers.SerializerMethodField()
    neckline = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()

    class Meta:
        model = ClothesInfo
        fields = ['id', 'length', 'sleeve_length', 'neckline', 'fit', 'style']

    def get_length(self, obj):
        try:
            cleaned_length = obj.length.strip("[]").replace("'", "")
            return [len.strip() for len in cleaned_length.split(',')] if cleaned_length else []
        except Exception as e:
            return []

    def get_sleeve_length(self, obj):
        try:
            cleaned_sleeve_length = obj.sleeve_length.strip("[]").replace("'", "")
            return cleaned_sleeve_length.strip() if cleaned_sleeve_length else []
        except Exception as e:
            return ""

    def get_neckline(self, obj):
        try:
            cleaned_neckline = obj.neckline.strip("[]").replace("'", "")
            return [nline.strip() for nline in cleaned_neckline.split(',')] if cleaned_neckline else []
        except Exception as e:
            return []

    def get_style(self, obj):
        try:
            cleaned_style = obj.style.strip("[]").replace("'", "")
            return [stl.strip() for stl in cleaned_style.split(',')] if cleaned_style else []
        except Exception as e:
            return []


# ShoesInfo Serializer
class ShoesInfoSerializer(serializers.ModelSerializer):
    heel_height = serializers.CharField()
    additional_description = serializers.CharField()
    footwear_style = serializers.SerializerMethodField()
    class Meta:
        model = ShoesInfo
        fields = ['id', 'heel_height', 'additional_description', 'footwear_style']

    def get_additional_description(self, obj):
        try:
            return json.loads(obj.additional_description) if obj.additional_description else []
        except json.JSONDecodeError:
            return [obj.additional_description]

    def get_footwear_style(self, obj):
        try:
            cleaned_footwear_style = obj.neckline.strip("[]").replace("'", "")
            return [footstl.strip() for footstl in cleaned_footwear_style.split(',')] if cleaned_footwear_style else []
        except Exception as e:
            return []


# Product Serializer
class ProductDetailsSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'gender', 'first_age', 'last_age', 'category', 'age_group',
                  'price', 'image_url', 'sizes', 'colors', 'description', 'pattern', 'nice_to_know']

    def get_sizes(self, obj):
        try:
            # Clean up the string format to replace single quotes and strip brackets
            cleaned_sizes = obj.sizes.strip("[]").replace("'", "")
            # Split the string by commas and strip whitespace to get the list of sizes
            return [size.strip() for size in cleaned_sizes.split(',')] if cleaned_sizes else []
        except Exception as e:
            return []

    def get_colors(self, obj):
        try:
            cleaned_colors = obj.colors.strip("[]").replace("'", "")
            return [color.strip() for color in cleaned_colors.split(',')] if cleaned_colors else []
        except Exception as e:
            return []
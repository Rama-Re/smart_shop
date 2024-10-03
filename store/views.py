from django.shortcuts import render
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from deepface import DeepFace
from .models import User
from .serializers import UserSerializer


class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract data from request
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            image = request.FILES.get('face_image')
            face_image = request.data.get('face_image_path')
            face_embedding = request.data.get('face_embedding')
            username = request.data.get('username')

            # Check if the username is unique
            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if image is None:
                return Response({"error": "No face image provided"}, status=status.HTTP_400_BAD_REQUEST)

            temp_image_path = default_storage.save(f"temp_images/{image.name}", ContentFile(image.read()))
            temp_image_full_path = os.path.join(default_storage.location, temp_image_path)

            # Analyze image to get gender and age
            objs = DeepFace.analyze(img_path=temp_image_full_path, actions=['age', 'gender'])
            age = objs[0]['age']
            gender = objs[0]['dominant_gender']

            # Prepare user data
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "face_image": face_image,
                "face_embedding": face_embedding,
                "username": username,
                "gender": gender,
                "age": age,
                "balance": 500  # Default balance
            }

            # Use serializer to validate and save the user
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                if os.path.exists(temp_image_full_path):
                    os.remove(temp_image_full_path)
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

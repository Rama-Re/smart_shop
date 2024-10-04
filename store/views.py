from django.shortcuts import render
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from deepface import DeepFace
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .recommendation_system import recommend_by_gender_and_age
from .authentication import UsernameAuthentication


# class RegisterView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Extract data from request
#             first_name = request.data.get('first_name')
#             last_name = request.data.get('last_name')
#             image = request.FILES.get('face_image')
#             face_image_path = request.data.get('face_image_path')
#             face_embedding = request.data.get('face_embedding')
#             username = request.data.get('username')
#
#             # Check if the username is unique
#             if User.objects.filter(username=username).exists():
#                 return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
#             if image is None:
#                 return Response({"error": "No face image provided"}, status=status.HTTP_400_BAD_REQUEST)
#             temp_image_path = default_storage.save(f"temp_images/{image.name}", ContentFile(image.read()))
#             temp_image_full_path = os.path.join(default_storage.location, temp_image_path)
#
#             # Analyze image to get gender and age
#             objs = DeepFace.analyze(img_path=temp_image_full_path, actions=['age', 'gender'])
#             age = objs[0]['age']
#             gender = objs[0]['dominant_gender']
#
#             if gender == 'Man':
#                 gender = 'M'
#             else:
#                 gender = 'F'
#             # Prepare user data
#             user_data = {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "face_image_path": face_image_path,
#                 "face_embedding": face_embedding,
#                 "username": username,
#                 "gender": gender,
#                 "age": age,
#                 "balance": 500  # Default balance
#             }
#
#             # Use serializer to validate and save the user
#             serializer = UserSerializer(data=user_data)
#             if serializer.is_valid():
#                 serializer.save()
#                 if os.path.exists(temp_image_full_path):
#                     os.remove(temp_image_full_path)
#                 return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetFaceEmbeddingView(APIView):
    authentication_classes = [UsernameAuthentication]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
            return Response({
                'face_embedding': user.face_embedding
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    authentication_classes = [UsernameAuthentication]  # Use the custom authentication class

    def post(self, request, *args, **kwargs):
        # Authenticate the user using the custom UsernameAuthentication class
        user = UsernameAuthentication().authenticate(request)

        if user is not None:
            # Generate JWT token
            refresh = RefreshToken.for_user(user[0])  # user[0] is the authenticated user
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user[0].username,
                'first_name': user[0].first_name,
                'last_name': user[0].last_name,
                'gender': user[0].gender,
                'age': user[0].age,
                'balance': user[0].balance
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Get the user from the request token
        user = request.user
        print(user)

        user_profile = UserSerializer(user).data

        return Response({
            'user_profile': user_profile
        })


class ShowProductsView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Get the user from the request token
        user = request.user

        user_gender = user.gender
        user_age = int(user.age)
        print(user_gender, user_age)
        # Fetch all products from the database
        all_products = Product.objects.all()

        # Call the recommendation function to filter products by gender and age
        recommended_products = recommend_by_gender_and_age(user_gender, user_age, all_products, top_n=376)
        # Use a serializer for the products
        product_list = ProductsShowSerializer(recommended_products, many=True).data

        return Response({
            'recommended_products': product_list
        })


class ShowProductView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        first_name = request.data.get('product_id')
        user_profile = UserSerializer(user).data

        return Response({
            'user_profile': user_profile
        })
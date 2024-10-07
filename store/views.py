from django.shortcuts import render
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from deepface import DeepFace
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .recommendation_system import *
from .authentication import UsernameAuthentication


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract data from request
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            image = request.FILES.get('face_image')
            face_image_path = request.data.get('face_image_path')
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

            if gender == 'Man':
                gender = 'M'
            else:
                gender = 'F'
            # Prepare user data
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "face_image_path": face_image_path,
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
        product_id = request.data.get('product_id')

        try:
            # Fetch the product by ID
            product = Product.objects.get(id=product_id)
            # product.sizes = product.get_sizes()
            # Serialize the product with its related info
            product_details = ProductDetailsSerializer(product).data
            if product.product_type == 'C':
                clothes_info = ClothesInfo.objects.get(product_id=product_id)
                clothes_details = ClothesInfoSerializer(clothes_info).data
                product_details.update(clothes_details)
            else:
                shoes_info = ShoesInfo.objects.get(product_id=product_id)
                shoes_details = ShoesInfoSerializer(shoes_info).data
                product_details.update(shoes_details)

            return Response({
                'product_details': product_details
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmotionView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]
    def post(self, request, *args, **kwargs):
        try:
            image = request.FILES.get('face_image')

            if image is None:
                return Response({"error": "No face image provided"}, status=status.HTTP_400_BAD_REQUEST)
            temp_image_path = default_storage.save(f"temp_images/{image.name}", ContentFile(image.read()))
            temp_image_full_path = os.path.join(default_storage.location, temp_image_path)

            # Analyze image to get gender and age
            objs = DeepFace.analyze(img_path=temp_image_full_path, actions=['emotion'])
            emotion = objs[0]['dominant_emotion']

            user_data = {
                "emotion": emotion
            }

            if os.path.exists(temp_image_full_path):
                os.remove(temp_image_full_path)
                return Response(user_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "couldn't get face emotion"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FilteredProductsView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def post(self, request):

        gender = request.data.get('gender')
        age = request.data.get('age')
        # Fetch all products from the database
        all_products = Product.objects.all()

        # Call the recommendation function to filter products by gender and age
        recommended_products = filter_by_gender_and_age(gender, age, all_products)
        # Use a serializer for the products
        product_list = ProductsShowSerializer(recommended_products, many=True).data

        return Response({
            'recommended_products': product_list
        })


class LowerPriceProductsView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        clothes_info = None
        shoes_info = None
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)

        if product.product_type == 'C':
            clothes_info = product.clothesinfo
        else:
            shoes_info = product.shoesinfo
        # Fetch all products from the database
        all_products = Product.objects.all()
        similar_products = recommend_similar_products(product, all_products, clothes_info, shoes_info)

        recommended_products = recommend_lower_priced_products(product, similar_products)
        # Use a serializer for the products
        product_list = ProductsShowSerializer(recommended_products, many=True).data

        return Response({
            'recommended_products': product_list
        })


class DescriptionFilteredProductsView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        description = request.data.get('description')

        # Fetch all products from the database
        all_products = Product.objects.all()

        recommended_products = recommend_based_on_text(description, all_products)
        # Use a serializer for the products
        product_list = ProductsShowSerializer(recommended_products, many=True).data

        return Response({
            'recommended_products': product_list
        })


class SimilarProductsView(APIView):
    # Use token authentication and ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        clothes_info = None
        shoes_info = None
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)

        if product.product_type == 'C':
            clothes_info = product.clothesinfo
        else:
            shoes_info = product.shoesinfo
        # Fetch all products from the database
        all_products = Product.objects.all()

        similar_products = recommend_similar_products(product, all_products, clothes_info, shoes_info)

        product_list = ProductsShowSerializer(similar_products, many=True).data

        return Response({
            'recommended_products': product_list
        })


## CartViews
class AddToCartView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        size = request.data.get('size')
        color = request.data.get('color')
        # count = request.data.get('count')

        try:
            product = Product.objects.get(id=product_id)
            try:
                cart = Cart.objects.get(product_id=product_id, user=request.user, size=size, color=color)
            except Cart.DoesNotExist:
                # Create a new cart item
                cart_item = Cart.objects.create(
                    user=user,
                    product=product,
                    size=size,
                    color=color,
                    count=1
                )
                return Response({"message": "Product added to cart successfully."}, status=status.HTTP_201_CREATED)

            cart.count = cart.count + 1
            cart.save()
            return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetCartView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditCartView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        cart_id = request.data.get('cart_id')
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddToCartSerializer(cart, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCartView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        cart_id = request.data.get('cart_id')

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.delete()
            return Response({"message": "Cart deleted successfully."}, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


class CheckoutView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        subtotal = sum(cart.product.price * cart.count for cart in carts)
        total_count = sum(cart.count for cart in carts)

        if total_count == 2:
            sale = 15
        elif total_count > 2:
            sale = 25
        else:
            sale = 0

        total = subtotal - (subtotal * sale / 100)

        serializer = CartSerializer(carts, many=True)

        return Response({
            'carts': serializer.data,
            'subtotal': subtotal,
            'sale': sale,
            'total': total
        }, status=status.HTTP_200_OK)


class PayView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)

        subtotal = sum(cart.product.price * cart.count for cart in carts)
        total_count = sum(cart.count for cart in carts)

        if total_count == 2:
            sale = 15
        elif total_count > 2:
            sale = 25
        else:
            sale = 0

        total = subtotal - (subtotal * sale / 100)

        if user.balance >= total:
            user.balance -= total
            user.save()

            carts.delete()

            serializer = CartSerializer(carts, many=True)

            return Response({
                'carts': serializer.data,
                'subtotal': subtotal,
                'sale': sale,
                'total': total,
                'message': "Payment successful."
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

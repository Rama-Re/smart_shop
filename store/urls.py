from django.contrib import admin
from django.urls import path, include
from .views import *
from django.contrib.auth.middleware import AuthenticationMiddleware

urlpatterns = [
    # path('register', RegisterView.as_view()),
    path('get_face_embedding', GetFaceEmbeddingView.as_view()),
    path('login', LoginView.as_view()),
    path('user_profile', UserProfileView.as_view()),
    path('show_products', ShowProductsView.as_view()),
    path('show_product', ShowProductView.as_view()),
]

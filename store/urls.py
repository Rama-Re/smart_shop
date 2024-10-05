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
    path('show_product_details', ShowProductView.as_view()),
    # path('face_emotion', EmotionView.as_view()),
    path('filter_products', FilteredProductsView.as_view()),
    path('lower_price_products', LowerPriceProductsView.as_view()),
    path('filter_by_description_products', DescriptionFilteredProductsView.as_view()),
    path('similar_products', SimilarProductsView.as_view()),


    path('add_to_cart', AddToCartView.as_view(), name='add_to_cart'),
    path('get_cart', GetCartView.as_view(), name='get_cart'),
    path('edit_cart', EditCartView.as_view(), name='edit_cart'),
    path('delete_cart', DeleteCartView.as_view(), name='delete_cart'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('pay', PayView.as_view(), name='pay'),
]

from django.contrib import admin
from .models import User, Cart, Product, ClothesInfo, ShoesInfo

admin.site.register(User)
admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(ClothesInfo)
admin.site.register(ShoesInfo)

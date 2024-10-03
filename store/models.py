import json

from django.db import models


# User Model
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    face_image = models.TextField()
    face_embedding = models.TextField()  # This could be a long string or JSON representation
    username = models.CharField(max_length=100, unique=True)
    gender = models.CharField(max_length=100)
    age = models.CharField(max_length=3)
    balance = models.FloatField()

    def __str__(self):
        return f"{self.username}"


# Product Model
class Product(models.Model):
    gender = models.CharField(max_length=100)
    first_age = models.FloatField()
    last_age = models.FloatField()
    product_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    age_group = models.CharField(max_length=100)
    price = models.FloatField()
    image_url = models.URLField(max_length=500)
    sizes = models.CharField(max_length=200)
    colors = models.CharField(max_length=400)
    description = models.TextField()
    pattern = models.CharField(max_length=200)
    nice_to_know = models.TextField()

    def set_sizes(self, size_list):
        self.sizes = json.dumps(size_list)

    def get_sizes(self):
        return json.loads(self.sizes)

    def set_colors(self, color_list):
        self.colors = json.dumps(color_list)

    def get_colors(self):
        return json.loads(self.colors)

    def __str__(self):
        return f"{self.product_name} - {self.category}"


# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    count = models.IntegerField()

    def set_sizes(self, size_list):
        self.sizes = json.dumps(size_list)

    def get_sizes(self):
        return json.loads(self.sizes)

    def set_colors(self, color_list):
        self.colors = json.dumps(color_list)

    def get_colors(self):
        return json.loads(self.colors)

    def __str__(self):
        return f"Cart for {self.user.username}"


# Clothes Info Model
class ClothesInfo(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    length = models.CharField(max_length=200)
    sleeve_length = models.CharField(max_length=200)
    neckline = models.CharField(max_length=200)
    fit = models.CharField(max_length=200)
    style = models.CharField(max_length=200)

    def set_length(self, length_list):
        self.length = json.dumps(length_list)

    def get_length(self):
        return json.loads(self.length)

    def set_sleeve_length(self, sleeve_length_list):
        self.sleeve_length = json.dumps(sleeve_length_list)

    def get_sleeve_length(self):
        return json.loads(self.sleeve_length)

    def set_neckline(self, neckline_list):
        self.neckline = json.dumps(neckline_list)

    def get_neckline(self):
        return json.loads(self.neckline)

    def set_style(self, style_list):
        self.style = json.dumps(style_list)

    def get_style(self):
        return json.loads(self.style)

    def __str__(self):
        return f"Clothes Info for {self.product.product_name}"


# Shoes Info Model
class ShoesInfo(models.Model):
    HEEL_HEIGHT_CHOICES = [
        ('no heel', 'No Heel'),
        ('high heel', 'High Heel'),
        ('low heel', 'Low Heel'),
        ('not specified', 'Not specified'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    heel_height = models.CharField(max_length=100)
    additional_description = models.CharField(max_length=200)
    footwear_style = models.CharField(max_length=200)

    def set_footwear_style(self, footwear_style_list):
        self.footwear_style = json.dumps(footwear_style_list)

    def get_footwear_style(self):
        return json.loads(self.footwear_style)

    def __str__(self):
        return f"Shoes Info for {self.product.product_name}"

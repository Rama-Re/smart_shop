import json

from django.db import migrations, models
import django.db.models.deletion
import csv
import ast


def load_data(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    ClothesInfo = apps.get_model('store', 'ClothesInfo')
    gender_mapping = {
        'unisex': 'U',
        'girl': 'F',
        'boy': 'M',
        'women': 'F',
        'men': 'M'
    }
    with open('data/clothes_data v3.csv', encoding='utf-8') as file:
        # reader = csv.DictReader(file)
        reader = csv.reader(file)
        header = next(reader)  # skip header row
        for row in reader:
            gender_value = row[0].strip().lower()  # Ensure case consistency
            gender = gender_mapping.get(gender_value, None)  # Use None if not found

            if gender is None:
                print(f"Unknown gender: {gender_value}")  # Optional: log unknown gender

            product = Product.objects.create(
                gender=gender,
                first_age=float(row[7]),  # 'First Age'
                last_age=float(row[8]),
                product_type='C',  # Assuming 'C' for clothes, adjust as needed
                category=row[2],  # 'Category'
                product_name=row[3],  # 'Product Name'
                age_group=row[1],  # 'Age Groups'
                price=float(row[4]),  # 'Product Price'
                image_url=row[5],  # 'Image_url'
                sizes=row[9],  # Convert string representation of list to list
                colors=row[6],  # Convert string representation of list to list, 'colors'
                description=row[10],
                pattern=row[13],
                nice_to_know=row[14]  # Assuming this column may have data
            )

            ClothesInfo.objects.create(
                product=product,
                length='[' + row[11] + ']',
                sleeve_length='[' + row[12] + ']',
                neckline='[' + row[16] + ']',
                fit=row[17],
                style='[' + row[15] + ']'
            )


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]

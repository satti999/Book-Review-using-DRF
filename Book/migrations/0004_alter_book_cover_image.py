# Generated by Django 5.1.5 on 2025-01-30 08:37

import Book.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Book', '0003_book_likes_book_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to=Book.models.upload_to),
        ),
    ]

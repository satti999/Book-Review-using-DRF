# Generated by Django 5.1.5 on 2025-01-29 11:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Book', '0002_delete_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='likes',
            field=models.IntegerField(default=0, help_text='Number of likes for this book.'),
        ),
        migrations.AddField(
            model_name='book',
            name='rating',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
            preserve_default=False,
        ),
    ]

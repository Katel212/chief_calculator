# Generated by Django 4.2.1 on 2023-06-05 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipe_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='price_changed',
            field=models.BooleanField(default=False),
        ),
    ]

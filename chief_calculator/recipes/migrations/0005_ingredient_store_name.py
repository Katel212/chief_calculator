# Generated by Django 4.2.1 on 2023-06-15 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_rename_price_recipe_cost_price_recipe_final_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='store_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
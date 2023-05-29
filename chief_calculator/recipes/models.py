from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.JSONField()
    notes = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    from_store = models.ForeignKey('Store', to_field='name', on_delete=models.SET_NULL, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('recipe_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    url = models.URLField(blank=True, null=True)
    recipe = models.ForeignKey('Recipe', to_field='id', on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('ingredient-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.id


class Store(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    delivery_info = models.TextField()
    min_order = models.IntegerField(null=True, blank=True)
    delivery_url = models.URLField()
    delivery_service = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('store-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.name

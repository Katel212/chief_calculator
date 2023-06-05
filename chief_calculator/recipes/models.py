from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    from_store = models.CharField(max_length=100, null=True, blank=True)
    cost_price = models.FloatField(blank=True, null=True)
    final_price = models.FloatField(blank=True, null=True)
    price_changed = models.BooleanField(default=False)

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
        return str(self.id)

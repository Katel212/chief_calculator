# forms.py
from django.core.exceptions import ValidationError

from .models import Ingredient, Recipe
from django.forms import ModelForm
from django import forms


class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "quantity"]


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'notes','is_published']
        labels = {
            "name": "Название",
            "notes": "Заметки",
            "is_published": "Опубликовать"
        }

class SubmitPriceForm(forms.Form):
    price = forms.FloatField(label="")

    def clean_price(self):
        data = self.cleaned_data['price']
        if data <= 0:
            raise ValidationError('Цена должна быть больше нуля')
        return data

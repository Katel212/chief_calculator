# forms.py
from .models import Ingredient, Recipe
from django.forms import modelformset_factory, ModelForm

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

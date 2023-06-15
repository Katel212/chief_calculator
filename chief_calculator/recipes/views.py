from django.contrib.auth.decorators import login_required

from .forms import RecipeForm, IngredientForm, SubmitPriceForm
from .parser import parser_sdelay_tort as pst
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Recipe, Ingredient
from django.forms import formset_factory
from django.views.generic import (
    ListView, TemplateView,
)
from django.core.cache import cache

from users import views

from .parser import parser_tortomaster as ptm
from .parser import parser_pekar as ppk


def index(request):
    return render(request, 'recipes/index.html')


@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    recipes = Recipe.objects.filter(user=user.id)
    return render(request, 'recipes/profile.html', context={'user': user, 'recipes': recipes})


def show_recipe(request, id_item):
    recipe = Recipe.objects.get(id=id_item)
    ingredients = cache.get(f'recipe_{recipe.id}')
    if not ingredients:
        ingredients = Ingredient.objects.filter(recipe=recipe.id)
    # если авторизован, тогда есть смысл проверять принадлежность
    if request.user.is_authenticated:
        belonging = True if recipe.user.id == request.user.id else False

        context = {'recipe': recipe, 'ingredients': ingredients, "belonging": belonging}
        # если метод POST, то точно не принадлежит, добавляем рецепт и отображаем с кнопкой "добавлен"
        if request.method == "POST":
            new_recipe = Recipe(name=recipe.name, notes=recipe.notes,
                                user=request.user)
            new_recipe.save()
            context["belonging"] = True
            context["recipe"] = Recipe.objects.get(id=new_recipe.id)
        return render(request, 'recipes/recipe_detail.html',
                      context=context)
    # если не авторизован
    else:
        # и попытался добавить рецепт, то редирект на страницу логина
        if request.method == "POST":
            return redirect(views.register)
        else:
            return render(request, 'recipes/recipe_detail.html',
                          context={'recipe': recipe, 'ingredients': ingredients, "belonging": False})


def recipe_price(request, id_item, store):
    recipe = Recipe.objects.get(id=id_item)
    if request.method == "POST":
        form = SubmitPriceForm(request.POST)
        if form.is_valid():
            s = cache.get('stores_info')

            bs = cache.get('best_store')
            recipe.cost_price = s[bs].cart_price
            recipe.final_price = form.cleaned_data['price']
            recipe.from_store = bs
            recipe.save()
            return redirect('recipe_detail', id_item=recipe.id)
    else:
        ingredients = Ingredient.objects.filter(recipe=recipe.id)
        ingredients_dict = {}
        for i in ingredients:
            ingredients_dict[i.name] = i.quantity
        if store == 'None':
            stores_info = {}
            st_info = pst.ParserSdelayTort(ingredients_dict)
            st_info.get_ingredients_info()
            stores_info['Сделай торт'] = st_info
            tm_info = ptm.ParserTortomaster(ingredients_dict)
            tm_info.get_ingredients_info()
            stores_info['Тортомастер'] = tm_info

            pk_info = ppk.ParserPekarKonditer(ingredients_dict)
            pk_info.get_ingredients_info()
            stores_info['Пекарь кондитер'] = pk_info

            best_store = best_offer(stores_info)
            cache.set('stores_info', stores_info, 86400)
            cache.set('best_store', best_store, 86400)

            form = SubmitPriceForm(initial={"price": stores_info[best_store].recommend_price})

            return render(request, 'recipes/recipe_price.html', context={'recipe': recipe,
                                                                         'stores_info': stores_info,
                                                                         'best_store': stores_info[best_store],
                                                                         'form': form})
        else:
            s = cache.get('stores_info')
            cache.set('best_store', store, 86400)

            form = SubmitPriceForm(initial={"price": s[store].recommend_price})

            return render(request, 'recipes/recipe_price.html', context={'recipe': recipe,
                                                                         'stores_info': s,
                                                                         'best_store': s[store],
                                                                         'form': form})


def best_offer(stores_info: dict):
    store = None
    best_price = 10000
    best_quantity = 0
    for s in stores_info.items():
        store_object = s[1]
        filtered_ingredients = list(filter(lambda x: x.name != 'не найден', store_object.final_ingredients.values()))
        if len(filtered_ingredients) > best_quantity:
            best_price = store_object.cart_price_per_gr
            best_quantity = len(filtered_ingredients)
            store = s[0]
        elif len(filtered_ingredients) == best_quantity and store_object.cart_price_per_gr < best_price:
            best_price = store_object.cart_price
            store = s[0]
    return store


def add_recipe(request):
    IFS = formset_factory(IngredientForm, extra=3)
    if request.method == 'POST':
        ingredients_formset = IFS(request.POST, prefix='ingredients')
        recipe_form = RecipeForm(request.POST)
        if recipe_form.is_valid():
            if ingredients_formset.is_valid():
                new_recipe = recipe_form.save(commit=False)
                new_recipe.user = request.user
                new_recipe.save()
                ingr_list = []
                i = 0
                for f in ingredients_formset:
                    if f.data.get(f'ingredients-{i}-name'):
                        new_ingredient = f.save(commit=False)
                        new_ingredient.recipe = new_recipe
                        new_ingredient.save()
                        ingr_list.append(new_ingredient)
                    i += 1
                cache.set(f'recipe_{new_recipe.id}', ingr_list, 60 * 60 * 24 * 3)
                return redirect('recipe_detail', id_item=new_recipe.id)
            context = {"ingredients_formset": ingredients_formset, "recipe_form": recipe_form}
            return render(request, 'recipes/recipe_form.html', context=context)
    else:
        ingredients_formset = IFS(prefix='ingredients')
        recipe_form = RecipeForm()
        context = {"ingredients_formset": ingredients_formset, "recipe_form": recipe_form}
        return render(request, 'recipes/recipe_form.html', context=context)


class HomeView(ListView):
    model = Recipe
    template_name = 'recipes/index.html'
    paginate_by = 10
    context_object_name = 'recipes'

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)
        return queryset

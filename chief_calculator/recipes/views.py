from django.contrib.auth.decorators import login_required
from .parser import parser_sdelay_tort as pst
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Recipe, Ingredient, Store
from django.views.generic import (
    ListView,
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
    # если авторизован, тогда есть смысл проверять принадлежность
    if request.user.is_authenticated:
        belonging = True if recipe.user.id == request.user.id else False
        context = {'recipe': recipe, 'ingredients': recipe.ingredients, "belonging": belonging}
        # если метод POST, то точно не принадлежит, добавляем рецепт и отображаем с кнопкой "добавлен"
        if request.method == "POST":
            new_recipe = Recipe(name=recipe.name,
                                ingredients=recipe.ingredients, notes=recipe.notes,
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
                          context={'recipe': recipe, 'ingredients': recipe.ingredients, "belonging": False})


def recipe_price(request, id_item, store):
    recipe = Recipe.objects.get(id=id_item)
    if store == 'None':
        stores_info = {}
        st_info = pst.ParserSdelayTort(recipe.ingredients)
        st_info.get_ingredients_info()
        print("tm=", st_info.cart_price)
        stores_info['Сделай торт'] = st_info
        tm_info = ptm.ParserTortomaster(recipe.ingredients)
        tm_info.get_ingredients_info()
        print("tm=", tm_info.cart_price)
        stores_info['Тортомастер'] = tm_info

        pk_info = ppk.ParserPekarKonditer(recipe.ingredients)
        pk_info.get_ingredients_info()
        print("pk=", pk_info.cart_price)
        stores_info['Пекарь кондитер'] = pk_info

        best_store = best_offer(stores_info)
        cache.set('stores_info', stores_info, 86400)

        return render(request, 'recipes/recipe_price.html', context={'recipe': recipe,
                                                                     'stores_info': stores_info,
                                                                     'best_store': stores_info[best_store]})
    else:
        s = cache.get('stores_info')
        print(s)
        return render(request, 'recipes/recipe_price.html', context={'recipe': recipe,
                                                                     'stores_info': s,
                                                                     'best_store': s[store]})


def best_offer(stores_info: dict):
    store = None
    best_price = 10000
    best_quantity = 0
    for s in stores_info.items():
        store_object = s[1]
        filtered_ingredients = list(filter(lambda x: x.name != 'не найден', store_object.final_ingredients))
        if len(filtered_ingredients) > best_quantity:
            best_price = store_object.cart_price_per_gr
            best_quantity = len(filtered_ingredients)
            store = s[0]
        elif len(filtered_ingredients) == best_quantity and store_object.cart_price_per_gr < best_price:
            best_price = store_object.cart_price
            store = s[0]
        print(store)
    return store


class HomeView(ListView):
    model = Recipe
    template_name = 'recipes/index.html'
    paginate_by = 10
    context_object_name = 'recipes'

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)
        return queryset

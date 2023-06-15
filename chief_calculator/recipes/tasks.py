from background_task import background
from .parser import parser_sdelay_tort as pst
from .parser import parser_tortomaster as ptm
from .parser import parser_pekar as ppk

from .models import Recipe, Ingredient


@background(schedule=1)
def check_price(recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    ingredients = Ingredient.objects.filter(recipe=recipe_id)
    parser = None
    if recipe.from_store == "Сделай торт":
        parser = pst.ParserSdelayTort({})
    elif recipe.from_store == "Тортомастер":
        parser = ptm.ParseTortomaster({})
    elif recipe.from_store == "Пекарь кондитер":
        parser = ppk.ParserPekarKonditer({})
    for i in ingredients:
        if not parser.check_ingredient_price(i):
            recipe.price_changed = True



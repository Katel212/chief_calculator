import time
import re

import requests
from bs4 import BeautifulSoup
from ..models import Ingredient as IngredientModel

from .parser_helper import ParserIngredients, Ingredient


class ParserPekarKonditer(ParserIngredients):

    def calculate_cart_price(self):
        for k, v in self.raw_ingredients.items():
            self.cart_price += self.final_ingredients[k].price_per_gr * v
        self.cart_price_per_gr = sum(
            x.price_per_gr for x in list(filter(lambda x: x.name != 'не найден', self.final_ingredients.values())))
        self.cart_price = int(self.cart_price)
        self.recommend_price = self.cart_price*3

    def check_ingredient_price(self, ingredient):
        ingredient = IngredientModel.objects.get(id=ingredient)
        content = requests.get(ingredient.url).content.decode("latin-1")
        soup = BeautifulSoup(content, "lxml")
        result = soup.find("div", class_="priup").contents[1].text

        if int(re.search(r'\d+', result).group(0)) != ingredient.price:
            return False
        else:
            return True
    def most_matching_ingredient(self):
        for i in self.raw_ingredients:
            needed_quantity = self.raw_ingredients[i]
            idx = 0
            min_difference = 1000
            for j in range(0, len(self.ingredients_info[i])):
                if self.ingredients_info[i][j].quantity is not None:
                    if 0 < self.ingredients_info[i][j].quantity - needed_quantity < min_difference:
                        idx = j
                        min_difference = self.ingredients_info[i][j].quantity - needed_quantity
            if idx == 0:
                self.ingredients_info[i] += [Ingredient("не найден", "0", "")]
            self.final_ingredients[i] = self.ingredients_info[i][idx]

    @staticmethod
    def get_search_string(ingredient_list: str):
        tmp_name = "+".join(ingredient_list.split())
        return f'https://rostov.konditermarket.ru/spage/?q={tmp_name}&s='

    def get_ingredients_info(self):
        for i in self.raw_ingredients.keys():
            while True:
                try:
                    content = requests.get(self.get_search_string(i)).content.decode("utf8")
                    break
                except:
                    time.sleep(5)
            soup = BeautifulSoup(content, "lxml")
            result = soup.findAll("div", class_="product-item")
            self.ingredients_info[i] = []
            real_name = i.split()[0].strip().lower()
            for r in result[0:5]:
                name = r.find("div", class_="product-item-title").contents[1].contents[0].lower().replace("\t", "").replace("\n","")
                if re.search(rf'(\w|\d|\s)*\s*{real_name}\s(\w|\d|\s)*', name):
                    url = f'https://rostov.konditermarket.ru{r.find("div", class_="product-item-title").contents[1].attrs["href"]}'
                    price = r.findAll("span", "product-item-price-current")[0].text.replace("\t", "").replace("\n","")
                    if re.search(r'(\w|\d|\s)*\s*руб\s*(\w|\d|\s)*', price):
                        if r.find('div', class_='product-item-button-container notinsale') is None:
                            self.ingredients_info[i] += [Ingredient(name, price, url)]
        self.most_matching_ingredient()
        self.calculate_cart_price()

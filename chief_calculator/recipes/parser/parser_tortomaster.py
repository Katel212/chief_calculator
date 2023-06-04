import re
import time

from .parser_helper import ParserIngredients, Ingredient
from bs4 import BeautifulSoup
import requests


class ParserTortomaster(ParserIngredients):

    def calculate_cart_price(self):
        for k, v in self.raw_ingredients.items():
            self.cart_price += self.final_ingredients[k].price_per_gr * v
        self.cart_price_per_gr = sum(x.price_per_gr for x in list(filter(lambda x: x.name != 'не найден', self.final_ingredients.values())))
        self.cart_price = int(self.cart_price)

        self.recommend_price = self.cart_price*3



    def __init__(self, ingredients):
        super().__init__(ingredients)

    @staticmethod
    def get_search_string(ingredient_list: str):
        tmp_name = "+".join(ingredient_list.split())
        r = f"https://rostov-na-donu.tortomaster.ru/catalog/?q={tmp_name}&s=Найти+товар"
        return r

    def get_ingredients_info(self):
        for i in self.raw_ingredients.keys():
            while True:
                try:
                    content = requests.get(self.get_search_string(i)).content.decode("utf8")
                    break
                except:
                    time.sleep(5)
            soup = BeautifulSoup(content, "lxml")
            result = soup.findAll("div", class_="catalog-item")
            self.ingredients_info[i] = []
            real_name = i.split()[0].strip().lower()
            for r in result[0:5]:
                name = r.find("div", class_="catalog-name-container").contents[1].contents[0].lower()
                if re.search(rf'(\w|\d|\s)*\s*{real_name}\s(\w|\d|\s)*', name):
                    url = f'https://rostov-na-donu.tortomaster.ru{r.find("div", class_="catalog-name-container").contents[1].attrs["href"]} '
                    price = r.findAll("span", "price")[0].text.replace(' ', '')
                    self.ingredients_info[i] += [Ingredient(name, price, url)]
        self.most_matching_ingredient()
        self.calculate_cart_price()


    def most_matching_ingredient(self):
        for i in self.raw_ingredients:
            needed_quantity = self.raw_ingredients[i]
            idx = 0
            min_difference = 1000
            for j in range(0, len(self.ingredients_info[i])):
                if 0 < self.ingredients_info[i][j].quantity - needed_quantity < min_difference:
                    idx = j
                    min_difference = self.ingredients_info[i][j].quantity - needed_quantity

            if idx == 0:
                self.ingredients_info[i] += [Ingredient("не найден", "0", "")]
            self.final_ingredients[i] = self.ingredients_info[i][idx]

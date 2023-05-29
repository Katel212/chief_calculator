import time
import re

import requests
from bs4 import BeautifulSoup

from .parser_helper import ParserIngredients, Ingredient


class ParserPekarKonditer(ParserIngredients):

    def calculate_cart_price(self):
        for i in self.final_ingredients:
            self.cart_price += i.price
        self.cart_price_per_gr = sum(
            x.price_per_gr for x in list(filter(lambda x: x.name != 'не найден', self.final_ingredients)))

    def most_matching_ingredient(self):
        for i in self.raw_ingredients:
            needed_quantity = self.raw_ingredients[i]
            idx = 0
            min_difference = 1000
            for j in range(0, len(self.ingredients_info[i])):
                if 0 < self.ingredients_info[i][j].quantity - needed_quantity < min_difference:
                    idx = j
            if idx == 0:
                self.ingredients_info[i] += [Ingredient("не найден", "0", "")]
            self.final_ingredients += [self.ingredients_info[i][idx]]

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
                name = r.find("div", class_="product-item-title").contents[1].contents[0]
                if re.search(rf'(\w|\d|\s)*\s*{real_name}\s(\w|\d|\s)*', name):
                    url = f'https://rostov.konditermarket.ru{r.find("div", class_="product-item-title").contents[1].attrs["href"]}'
                    price = r.findAll("span", "product-item-price-current")[0].text.replace(' ', '')
                    if 'руб' in price:
                        if r.findAll('div', class_='product-item-button-container notinsale') is None:
                            self.ingredients_info[i] += [Ingredient(name, price, url)]
        self.most_matching_ingredient()
        self.calculate_cart_price()

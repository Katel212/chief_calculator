from abc import ABC, abstractmethod

import re


class ParserIngredients(ABC):
    def __init__(self, ingredients: dict):
        self.raw_ingredients = ingredients
        self.ingredients_info = {}
        self.final_ingredients = []
        self.cart_price = 0
        self.cart_price_per_gr = 1000

    @staticmethod
    @abstractmethod
    def get_search_string(ingredient_list: str):
        pass

    @abstractmethod
    def get_ingredients_info(self):
        pass

    @abstractmethod
    def most_matching_ingredient(self):
        pass

    @abstractmethod
    def calculate_cart_price(self):
        pass


class Ingredient:
    def __init__(self, name, price, url):
        self.price = int(re.search(r'\d+', price).group(0))
        self.url = url
        self.name = name
        tmp = re.search(r'(\d+,?\d*\s?)(мл|л|г|кг|МЛ|Л|КГ|Г)', name)
        self.quantity = None
        self.price_per_gr = None
        if tmp is not None:
            self.normalize_quantity(tmp)
            self.price_per_gr = self.price / self.quantity


    def __str__(self):
        return f"{self.name}: {self.price}, {self.quantity}"

    def normalize_quantity(self, tmp):
        self.quantity = int(tmp.group(1))
        if tmp.group(2) == 'л' or tmp.group(2) == 'кг' or tmp.group(2) == 'Л' or tmp.group(2) == 'КГ':
            self.quantity *= 1000

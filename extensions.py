import json
import requests
from config import exchanges
from collections import defaultdict


class APIException(Exception):
    pass


class UserInfo:
    def __init__(self):
        self.f = "USD"
        self.t = "RUB"


class UserDB:
    def __init__(self):
        self.db = defaultdict(UserInfo)

    def change_from(self, user_id, val):
        self.db[user_id].f = val

    def change_to(self, user_id, val):
        self.db[user_id].t = val

    def get_pair(self, user_id):
        user = self.db[user_id]
        return user.f, user.t


class Convertor:
    @ staticmethod
    def get_price(*values):
        if len(values) != 3:
            raise APIException('Не верное колличекство параметров')
        quote, base, amount = values
        if quote == base:
            raise APIException(
                'Не возможно конвертировать одинаковые валюты {base}!')
        base_key = quote
        sym_key = base
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(
                f'Не удалось обработать количество {amount} (для дробной части используйте точку)!')

        r = requests.get(
            f"http://api.currencylayer.com/live?access_key=7c697178fb19cd4925471615ef465761")
        resp = json.loads(r.content)
        if base_key != 'USD' and sym_key != 'USD':
            simb1 = 'USD' + base_key
            simb2 = 'USD' + sym_key
            kurs1 = resp['quotes'][simb1]
            kurs2 = resp['quotes'][simb2]
            new_price = kurs2 / kurs1 * amount
            new_price = round(new_price, 3)
        elif base_key != 'USD':
            simb = sym_key + base_key
            new_price = 1 / resp['quotes'][simb] * amount
            new_price = round(new_price, 3)

        else:
            simb = base_key + sym_key
            new_price = resp['quotes'][simb] * amount
            new_price = round(new_price, 3)

        return new_price

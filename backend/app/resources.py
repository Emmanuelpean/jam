"""JAM resources such as currencies"""

from app import utils

CURRENCIES = utils.open_json("app/data/currencies.json")

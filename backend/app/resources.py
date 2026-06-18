"""JAM resources such as currencies"""

from app.utilities.files import open_json

CURRENCIES = open_json("app/data/currencies.json")

"""Router for miscellaneous endpoints like currencies and countries."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.utils import open_json

router = APIRouter(prefix="/others", tags=["others"])


@router.get("/currencies/", response_class=JSONResponse)
def get_currencies() -> list[dict]:
    """Get the list of currencies."""

    currencies = open_json("app/data/currencies.json")
    return currencies


@router.get("/countries/", response_class=JSONResponse)
def get_countries() -> list[dict]:
    """Get the list of countries."""

    countries = open_json("app/data/countries.json")
    return countries

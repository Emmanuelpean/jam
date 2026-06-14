"""FastAPI router for Scraping Favourite Filter endpoints."""

from app import models
from app.job_email_scraping import schemas
from app.routers.utility import generate_data_table_crud_router

scraping_favourite_filter_router = generate_data_table_crud_router(
    table_model=models.ScrapingFavouriteFilter,
    create_schema=schemas.ScrapingFilterCreate,
    update_schema=schemas.ScrapingFilterUpdate,
    out_schema=schemas.ScrapingFavouriteFilterOut,
    endpoint="scraping-favourite-filters",
    not_found_msg="Scraping Favourite Filter not found",
)

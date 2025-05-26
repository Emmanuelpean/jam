"""Main script"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import post, user, auth

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["https://www.google.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def main() -> dict:
    """main page"""

    return {"message": "Welcome to the API. Hello World!!!"}

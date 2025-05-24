from fastapi import HTTPException, Depends, APIRouter, status
from app import models
from sqlalchemy.orm import Session
from app import database, schemas, utils

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=201, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):

    # Get all users and check if the email is already registered
    users = db.query(models.User).all()
    if user.email in [u.email for u in users]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh the user to get the ID
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[schemas.UserOut])
def get_user(db: Session = Depends(database.get_db)):
    user = db.query(models.User).all()
    return user

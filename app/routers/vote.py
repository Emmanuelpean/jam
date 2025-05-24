from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from app import database, schemas, models, oauth2


router = APIRouter(prefix="/vote", tags=["vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if vote.value == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Vote already exists"
            )
        else:
            new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
            db.add(new_vote)
            print(new_vote)
            print("here")
            db.commit()
            print(new_vote)
            print("here")
            return new_vote
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        else:
            db.delete(found_vote)
            db.commit()
            return {"detail": "Vote removed"}

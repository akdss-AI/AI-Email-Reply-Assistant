from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models.session import Session as SessionModel
from schemas.session import SessionResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_session = SessionModel(
        user_id=current_user.id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("/sessions", response_model=list[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == current_user.id)
        .all()
    )

    return sessions
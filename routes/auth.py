from fastapi import APIRouter, HTTPException , status , Depends
from database import get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserResponse
from models.user import User
from auth import hash_password , verify_password, create_access_token 
from fastapi.security import OAuth2PasswordRequestForm
router=APIRouter()
@router.post('/signup' , response_model=UserResponse)
def create_user(user:UserCreate , db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==user.email).first()
    if  existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password=hash_password(user.password)
    db_user=User(
        email=user.email,
        hashed_password=hashed_password

    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
@router.post('/login' )
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    access_token=create_access_token({
        'sub':str(db_user.id)
    })
    return {
        'access_token':access_token,
        'token_type':'bearer'
    }

    
     





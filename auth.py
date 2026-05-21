from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, get_db
from models import User
from passlib.context import CryptContext # For password hashing
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # For OAuth2 flow
from jose import JWTError, jwt # For JWT encoding/decoding
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

router = APIRouter(tags=["auth"])
# Secret key for signing JWTs - **CHANGE THIS IN PRODUCTION!**
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256") # Hashing algorithm for JWT
# Password hashing context (using bcrypt)
dcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2PasswordBearer for handling token extraction from headers
oauth2_brearer = OAuth2PasswordBearer(tokenUrl="login")
# Pydantic model for user registration request body
class CreateUserRequest(BaseModel):
    username: str
    password: str
# Pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str
# Annotated dependency for easy type hinting in routes
db_dependancy = Annotated[Session, Depends(get_db)]
# --- API Endpoints ---
@router.post("/register", status_code=status.HTTP_201_CREATED )
async def create_user(db: db_dependancy, user: CreateUserRequest):
    try:
        # Hash the password before storing it
        create_user_model = User(
            username=user.username,
            password=dcrypt_context.hash(user.password))
        db.add(create_user_model) # Add the new user to the session
        db.commit() # Commit the transaction to save to DB
        return {"message": "User created successfully"} # Return a success message
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    try:
        # Authenticate user credentials
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
        # Create an access token for the authenticated user
        token = create_access_token(user.username, user.id, timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise # Allow FastAPI HTTPExceptions to bubble up normally
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
# --- Helper Functions ---
def authenticate_user(username:str, password: str, db):
    # Query database for user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False # User not found
    # Verify provided password against hashed password
    if not dcrypt_context.verify(password, user.password):
        return False # Password mismatch
    return user # User authenticated
def create_access_token(username:str, user_id : int, expires_delta: timedelta | None = None):
    # Payload for the JWT
    to_encode = {"sub": username, "id": user_id} # 'sub' is standard for subject
    # Set token expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) # Default 15 min expiry
    to_encode.update({"exp": expire}) # Add expiration to payload
    # Encode the JWT using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_brearer)]):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            # If payload is incomplete
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return {"username": username, "id": user_id} # Return user info from token
    except JWTError:
        # If token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )   
from datetime import timedelta
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# MongoDB connection (replace with your actual client setup)
# This assumes you have a get_database dependency or similar in your main app
class MongoDBSettings(BaseModel):
    uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/food_delivery")
    db_name: str = "food_delivery" # Assuming this is the database name

settings = MongoDBSettings()
client = AsyncIOMotorClient(settings.uri)
database = client[settings.db_name]
users_collection = database.users

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT secret and algorithm
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3 * 24 * 60 # 3 days

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable not set")

router = APIRouter()

# Pydantic models for request bodies and responses
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    _id: str
    name: str
    email: EmailStr

class LoginRegisterResponse(BaseModel):
    user: UserResponse
    token: str

class ErrorResponse(BaseModel):
    message: str

# Helper to create a JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = jwt.datetime.datetime.utcnow() + expires_delta
    else:
        expire = jwt.datetime.datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

# Helper to get the current user (e.g., from a dependency in authMiddleware.py)
# For now, we'll mock this or assume it's provided by a different file.
# In a real setup, `get_current_user` would decode the JWT and return the user object.
async def get_current_user_from_token_id(user_id: str):
    user_data = await users_collection.find_one({"_id": user_id}, {"password": 0}) # Exclude password
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(_id=str(user_data["_id"]), name=user_data["name"], email=user_data["email"])


# Utility for password strength (mimicking validator.isStrongPassword)
def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=[\]{};':\"\\|,.<>/?]", password):
        return False
    return True


@router.post("/login", response_model=LoginRegisterResponse, responses={
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def login_user(user_login: UserLogin):
    email = user_login.email
    password = user_login.password

    try:
        if not email or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter all fields")

        user = await users_collection.find_one({"email": email})

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")

        if not pwd_context.verify(password, user["password"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

        token_data = {"id": str(user["_id"])}
        token = create_access_token(token_data)

        return LoginRegisterResponse(
            user=UserResponse(_id=str(user["_id"]), name=user["name"], email=user["email"]),
            token=token
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/register", response_model=LoginRegisterResponse, responses={
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def register_user(user_register: UserRegister):
    name = user_register.name
    email = user_register.email
    password = user_register.password

    try:
        # Check if user already exists
        exists = await users_collection.find_one({"email": email})
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        if not name or not email or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter all fields")

        # Pydantic's EmailStr handles basic email validation, but `validator.isEmail` is more robust.
        # For simplicity, we'll rely on Pydantic and potentially add more checks if needed.
        # if not validator.isEmail(email): # This would require a Python equivalent library
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email")

        if not is_strong_password(password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a strong password")

        hashed_password = pwd_context.hash(password)

        new_user_data = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        result = await users_collection.insert_one(new_user_data)
        user_id = str(result.inserted_id)

        token_data = {"id": user_id}
        token = create_access_token(token_data)

        # Retrieve the newly created user (excluding password)
        created_user = await users_collection.find_one({"_id": result.inserted_id}, {"password": 0})
        if not created_user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")

        return LoginRegisterResponse(
            user=UserResponse(_id=str(created_user["_id"]), name=created_user["name"], email=created_user["email"]),
            token=token
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=UserResponse, responses={
    404: {"model": ErrorResponse},
    502: {"model": ErrorResponse}
})
async def get_user_info(current_user: UserResponse = Depends(get_current_user_from_token_id)):
    """
    Retrieves information about the authenticated user.
    The 'current_user' dependency is expected to extract the user ID from the token
    and fetch the user's details, then return a UserResponse object.
    """
    try:
        # The current_user dependency already fetches and validates the user.
        # We just return it.
        return current_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

# Note: The `get_current_user_from_token_id` function used in `get_user_info`
# is a placeholder. In a complete FastAPI application, this would be a dependency
# that decodes the JWT token from the Authorization header and fetches the
# corresponding user from the database. It would typically be defined
# in a separate `auth_dependencies.py` file or similar.

# Example of how the `get_current_user_from_token_id` dependency would be wired:
#
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#         user_id: str = payload.get("id")
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user_data = await users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
#         if not user_data:
#             raise HTTPException(status_code=401, detail="User not found")
#         return UserResponse(_id=str(user_data["_id"]), name=user_data["name"], email=user_data["email"])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Could not validate credentials")
#
# Then, in get_user_info:
# async def get_user_info(current_user: UserResponse = Depends(get_current_user)):
#    ...

# For this migration, we're assuming that the `req.user.id` from the original Express
# controller is conceptually handled by a dependency that provides the authenticated
# user's data (or at least their ID) to the FastAPI route. The `get_current_user_from_token_id`
# is a simplified representation for the purpose of demonstrating the controller logic.
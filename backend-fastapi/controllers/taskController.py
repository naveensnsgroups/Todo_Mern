from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

load_dotenv()

# Database connection using Motor
MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.taskmanager

# Pydantic models for request/response
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise ValueError("PyObjectId must be a string")
        return v

class TaskModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    description: str
    completed: bool = False
    userId: PyObjectId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str
        }
        schema_extra = {
            "example": {
                "title": "My Awesome Task",
                "description": "Do something really important.",
                "completed": False,
                "userId": "60c72b2f9c4f8d0015b6d1b2"
            }
        }

class UserInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    username: str
    email: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str
        }

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = None # Placeholder for actual OAuth2 scheme from auth router

# Dependency to get the current user
async def get_current_user_dependency(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await database.users.find_one({"_id": PyObjectId(user_id)})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserInDB(**user)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Email sending utility
def send_mail(email_to: str, subject: str, title: str, description: str):
    gmail_username = os.getenv("GMAIL_USERNAME")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if not gmail_username or not gmail_password:
        print("GMAIL_USERNAME or GMAIL_PASSWORD environment variables are not set.")
        return

    msg = MIMEText(f"<h1>Task added successfully</h1><h2>Title: {title}</h2><h3>Description: {description}</h3>", "html")
    msg["Subject"] = subject
    msg["From"] = gmail_username
    msg["To"] = email_to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_username, gmail_password)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskDelete(BaseModel):
    id: PyObjectId

@router.post("/addtask", status_code=status.HTTP_200_OK)
async def add_task(
    task_data: TaskCreate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    try:
        user = await database.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        new_task = TaskModel(
            title=task_data.title,
            description=task_data.description,
            completed=False,
            userId=current_user.id
        )
        
        result = await database.tasks.insert_one(new_task.dict(by_alias=True))
        
        send_mail(user["email"], "Task Added", task_data.title, task_data.description)
        return {"message": "Task added successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/removetask", status_code=status.HTTP_200_OK)
async def remove_task(
    task_delete_data: TaskDelete,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    try:
        result = await database.tasks.delete_one(
            {"_id": task_delete_data.id, "userId": current_user.id}
        )
        if result.deleted_count == 1:
            return {"message": "Task deleted successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not authorized to delete")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))

@router.get("/gettask", response_model=List[TaskModel], status_code=status.HTTP_200_OK)
async def get_task(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    try:
        tasks_cursor = database.tasks.find({"userId": current_user.id})
        tasks = await tasks_cursor.to_list(length=100) # Assuming max 100 tasks for now
        return [TaskModel(**task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))

# Placeholder for actual auth router where get_current_user_dependency is properly setup with OAuth2PasswordBearer
# from ..auth.auth import oauth2_scheme as actual_oauth2_scheme
# oauth2_scheme = actual_oauth2_scheme
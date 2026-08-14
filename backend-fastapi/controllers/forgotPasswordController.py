from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from models.user_model import UserModel  # Assuming UserModel is defined here

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection (replace with your actual connection setup)
async def get_database():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    database = client.get_database(os.getenv("DB_NAME", "todo_app")) # Default to "todo_app" if DB_NAME is not set
    try:
        yield database
    finally:
        client.close()

# Pydantic models for request bodies
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

@router.post("/forgotPassword")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate reset token
    reset_token = secrets.token_hex(20)
    
    # Update user with reset token
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"resetToken": reset_token}}
    )
    
    # Send email with reset token
    reset_url = f"https://todo-app-b96a5.web.app/resetPassword?token={reset_token}"
    
    gmail_username = os.getenv("GMAIL_USERNAME")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if not gmail_username or not gmail_password:
        print("GMAIL_USERNAME or GMAIL_PASSWORD environment variables are not set. Email will not be sent.")
        # Optionally, raise an error or return a message indicating email failure
        raise HTTPException(status_code=500, detail="Email service configuration error.")

    msg = MIMEText(f"<h1>Reset Password</h1><h2>Click on the link to reset your password</h2><h3>{reset_url}</h3>", "html")
    msg["From"] = "alok.yadav6000@gmail.com"
    msg["To"] = request.email
    msg["Subject"] = "Reset Password"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as transporter:
            transporter.login(gmail_username, gmail_password)
            transporter.send_message(msg)
        print(f"Email sent to {request.email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email.")
    
    return {"message": "A link to reset your password has been sent to your email."}

@router.post("/resetPassword")
async def reset_password(request: ResetPasswordRequest, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db["users"].find_one({"resetToken": request.token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Update password
    hashed_password = pwd_context.hash(request.password)
    
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"password": hashed_password, "resetToken": None}}
    )
    
    return {"message": "Password reset successful"}
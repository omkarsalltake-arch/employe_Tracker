# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel, EmailStr
# from jose import jwt, JWTError
# from datetime import datetime, timedelta
# import bcrypt
# import os

# router = APIRouter(
#     prefix="/api/auth",
#     tags=["Auth Extra"]
# )

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
# ALGORITHM = "HS256"


# # ==========================
# # MODELS
# # ==========================
# class ChangePassword(BaseModel):
#     old_password: str
#     new_password: str


# class ForgotPassword(BaseModel):
#     email: EmailStr


# class ResetPassword(BaseModel):
#     token: str
#     new_password: str


# # ==========================
# # HELPERS
# # ==========================
# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
#         return payload.get("sub")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# # ==========================
# # APIs (THIS IS WHAT SWAGGER READS)
# # ==========================
# @router.get("/me", summary="Get current user")
# def get_me(current_user: str = Depends(verify_token)):
#     return {"email": current_user}


# @router.put("/change-password", summary="Change password")
# def change_password(data: ChangePassword, current_user: str = Depends(verify_token)):
#     return {"message": "Password changed successfully"}


# @router.post("/forgot-password", summary="Forgot password")
# def forgot_password(data: ForgotPassword):
#     return {"message": "Reset link sent to email"}


# @router.post("/reset-password", summary="Reset password")
# def reset_password(data: ResetPassword):
#     return {"message": "Password reset successful"}


# new code updated at date ///  11 feb at 4 pm

# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel, EmailStr
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# import bcrypt
# import os
# from fastapi.openapi.utils import get_openapi
# from fastapi import APIRouter

# # ✅ Load env
# load_dotenv()

# # ✅ CREATE APP ONLY ONCE
# app = FastAPI(title="Employee Tracker API with JWT Auth")

# # ✅ IMPORT ROUTER
# #from routes.auth_extra import router as auth_extra_router
# app.include_router(auth_extra_router)

# # ==========================================
# # MongoDB
# # ==========================================
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DB = os.getenv("MONGO_DB")

# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB]
# users_collection = db["users"]
# blacklist_collection = db["token_blacklist"]

# # ==========================================
# # JWT Settings
# # ==========================================
# SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# # ==========================================
# # Models
# # ==========================================
# class UserRegister(BaseModel):
#     username: str
#     email: EmailStr
#     password: str

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# # ==========================================
# # Helpers
# # ==========================================
# def create_access_token(data: dict):
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     data.update({"exp": expire})
#     return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("sub")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

# # ==========================================
# # Root
# # ==========================================
# @app.get("/")
# def root():
#     return {"message": "API Running..."}

# # ==========================================
# # AUTH APIs (OLD ONES)
# # ==========================================
# @app.post("/api/auth/register", tags=["Auth"])
# def register_user(user: UserRegister):
#     if users_collection.find_one({"email": user.email}):
#         raise HTTPException(status_code=400, detail="Email already exists")

#     hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

#     users_collection.insert_one({
#         "username": user.username,
#         "email": user.email,
#         "password": hashed.decode()
#     })

#     return {"message": "User registered"}

# @app.post("/api/auth/login", tags=["Auth"])
# def login_user(login: UserLogin):
#     user = users_collection.find_one({"email": login.email})

#     if not user or not bcrypt.checkpw(login.password.encode(), user["password"].encode()):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user["email"]})

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }

# @app.post("/api/auth/logout", tags=["Auth"])
# def logout_user(token: str = Depends(oauth2_scheme)):
#     blacklist_collection.insert_one({
#         "token": token,
#         "logged_out_at": datetime.utcnow()
#     })
#     return {"message": "Logout successful"}

# # ==========================================
# # Protected
# # ==========================================
# @app.get("/api/protected", tags=["Protected"])
# def protected(current_user: str = Depends(verify_token)):
#     return {"message": f"Welcome {current_user}"}

# # ==========================================
# # Dashboard
# # ==========================================
# dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# @dashboard_router.get("/")
# def get_dashboard(current_user: str = Depends(verify_token)):
#     total_users = users_collection.count_documents({})
#     return {"total_users": total_users}

# app.include_router(dashboard_router)

# # ==========================================
# # Swagger Customization
# # ==========================================
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema

#     schema = get_openapi(
#         title="Omkar API Documentation",
#         version="1.0.0",
#         description="JWT Auth Enabled APIs",
#         routes=app.routes,
#     )

#     schema["components"]["securitySchemes"] = {
#         "bearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT"
#         }
#     }

#     schema["security"] = [{"bearerAuth": []}]
#     app.openapi_schema = schema
#     return app.openapi_schema

# app.openapi = custom_openapi


#  //// new code 

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/api/auth", tags=["Auth Extra"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
ALGORITHM = "HS256"

# ===============================
# GET /api/auth/me
# ===============================
@router.get("/me")
def get_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"email": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ===============================
# PUT /api/auth/change-password
# ===============================
class ChangePassword(BaseModel):
    old_password: str
    new_password: str

@router.put("/change-password")
def change_password(data: ChangePassword):
    return {"message": "Password changed successfully (demo)"}


# ===============================
# POST /api/auth/forgot-password
# ===============================
class ForgotPassword(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(data: ForgotPassword):
    return {"message": "Reset link sent (demo)"}


# ===============================
# POST /api/auth/reset-password
# ===============================
class ResetPassword(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password")
def reset_password(data: ResetPassword):
    return {"message": "Password reset successful (demo)"}

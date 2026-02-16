
# solve this corrs error....

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.openapi.utils import get_openapi
import bcrypt
import os

# ==========================================
# Load ENV
# ==========================================
load_dotenv()

app = FastAPI(title="Employee Tracker API - Production Ready")

# ==========================================
# ✅ PERMANENT CORS FIX
# ==========================================

FRONTEND_URL = os.getenv("FRONTEND_URL")

origins = [
    FRONTEND_URL,              # Production frontend (Render/Vercel)
    "http://localhost:3000",   # Local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ==========================================
# MongoDB Connection
# ==========================================
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

users_collection = db["users"]
restaurants_collection = db["restaurants"]
delivery_collection = db["delivery_boys"]
orders_collection = db["orders"]
blacklist_collection = db["token_blacklist"]

# ==========================================
# JWT Config
# ==========================================
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ==========================================
# Models
# ==========================================
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordModel(BaseModel):
    email: EmailStr

class ResetPasswordModel(BaseModel):
    token: str
    new_password: str

class UserInfoResponse(BaseModel):
    username: str
    email: EmailStr

# ==========================================
# Helpers
# ==========================================
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

# ==========================================
# 1️⃣ Root
# ==========================================
@app.get("/")
def root():
    return {"message": "API Running Successfully 🚀"}

# ==========================================
# 2️⃣ DB Test
# ==========================================
@app.get("/db-test")
def db_test():
    return {"status": "Database Connected"}

# ==========================================
# AUTH APIs
# ==========================================

# 3️⃣ Register
@app.post("/api/auth/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed.decode()
    })
    return {"message": "User registered successfully"}

# 4️⃣ Login
@app.post("/api/auth/login")
def login(data: UserLogin):
    user = users_collection.find_one({"email": data.email})
    if not user or not bcrypt.checkpw(data.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# 5️⃣ Logout
@app.post("/api/auth/logout")
def logout(token: str = Depends(oauth2_scheme)):
    blacklist_collection.insert_one({"token": token})
    return {"message": "Logged out successfully"}

# 6️⃣ Change Password
@app.post("/api/auth/change-password")
def change_password(data: ChangePasswordModel, current_user: str = Depends(verify_token)):
    user = users_collection.find_one({"email": current_user})
    if not bcrypt.checkpw(data.old_password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    new_hash = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt())
    users_collection.update_one({"email": current_user}, {"$set": {"password": new_hash.decode()}})
    return {"message": "Password changed successfully"}

# 7️⃣ Forgot Password
@app.post("/api/auth/forgot-password")
def forgot_password(data: ForgotPasswordModel):
    user = users_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    reset_token = create_access_token({"sub": data.email}, timedelta(hours=1))
    return {"reset_token": reset_token}

# 8️⃣ Reset Password
@app.post("/api/auth/reset-password")
def reset_password(data: ResetPasswordModel):
    payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    new_hash = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt())
    users_collection.update_one({"email": email}, {"$set": {"password": new_hash.decode()}})
    return {"message": "Password reset successfully"}

# 9️⃣ User Info
@app.get("/api/auth/user-info", response_model=UserInfoResponse)
def user_info(current_user: str = Depends(verify_token)):
    user = users_collection.find_one({"email": current_user})
    return {"username": user["username"], "email": user["email"]}

# ==========================================
# 1️⃣0️⃣ Protected
# ==========================================
@app.get("/api/protected")
def protected(current_user: str = Depends(verify_token)):
    return {"message": f"Welcome {current_user}"}

# ==========================================
# 1️⃣1️⃣ Dashboard
# ==========================================
@app.get("/api/dashboard")
def dashboard(current_user: str = Depends(verify_token)):
    return {
        "users": users_collection.count_documents({}),
        "restaurants": restaurants_collection.count_documents({}),
        "delivery_boys": delivery_collection.count_documents({}),
        "orders": orders_collection.count_documents({})
    }

# ==========================================
# 1️⃣2️⃣ List Restaurants
# ==========================================
@app.get("/api/restaurants")
def list_restaurants():
    return {"restaurants": list(restaurants_collection.find({}, {"_id": 0}))}

# ==========================================
# 1️⃣3️⃣ List Orders
# ==========================================
@app.get("/api/orders")
def list_orders():
    return {"orders": list(orders_collection.find({}, {"_id": 0}))}

# ==========================================
# Swagger Bearer Support
# ==========================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Omkar API Documentation",
        version="1.0.0",
        description="13 APIs with JWT + Production CORS",
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

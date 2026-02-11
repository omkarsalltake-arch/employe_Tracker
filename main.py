
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
import bcrypt
import os
from fastapi.openapi.utils import get_openapi
from fastapi import APIRouter
from routes.auth_extra import router as auth_extra_router

load_dotenv()

app = FastAPI(title="Employee Tracker API with JWT Auth")
app.include_router(auth_extra_router)  # INCLUDE YOUR AUTH ROUTER

# ==========================================
# Load .env
# ==========================================
load_dotenv()

# ==========================================
# MongoDB Connection
# ==========================================
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI or not MONGO_DB:
    raise RuntimeError("MONGO_URI or MONGO_DB is missing")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
users_collection = db["users"]
blacklist_collection = db["token_blacklist"]
restaurants_collection = db["restaurants"]
delivery_collection = db["delivery_boys"]
orders_collection = db["orders"]

# ==========================================
# JWT Settings
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
            raise HTTPException(status_code=401, detail="Invalid token data")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

# ==========================================
# Root Route
# ==========================================
@app.get("/")
def root():
    return {"message": "OS API is running ..."}

# ==========================================
# DB Test
# ==========================================
@app.get("/db-test")
def db_test():
    try:
        users_collection.find_one({})
        return {"status": "OK"}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# Auth Routes
# ==========================================
@app.post("/api/auth/register")
def register_user(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed.decode()
    })
    return {"message": "User registered", "email": user.email}

@app.post("/api/auth/login")
def login_user(login: UserLogin):
    user = users_collection.find_one({"email": login.email})
    if not user or not bcrypt.checkpw(login.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user["email"]})
    return {"message": "Login successful", "access_token": token, "token_type": "bearer"}

@app.post("/api/auth/logout", tags=["Auth"], summary="Logout user", description="Logout user by invalidating JWT token")
def logout_user(token: str = Depends(oauth2_scheme)):
    blacklist_collection.insert_one({
        "token": token,
        "logged_out_at": datetime.utcnow()
    })
    return {"message": "Logout successful"}

# ==========================================
# Protected Route
# ==========================================
@app.get("/api/protected", tags=["Protected"])
def protected(current_user: str = Depends(verify_token)):
    return {"message": f"Welcome {current_user}!"}

# ==========================================
# Dashboard Router
# ==========================================
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@dashboard_router.get("/", summary="Get Dashboard Analytics")
def get_dashboard(current_user: str = Depends(verify_token)):
    try:
        total_users = users_collection.count_documents({})

        total_restaurants = restaurants_collection.count_documents({})
        total_delivery_boys = delivery_collection.count_documents({})
        total_orders = orders_collection.count_documents({})

        pending_orders = orders_collection.count_documents({"status": "Pending"})
        completed_orders = orders_collection.count_documents({"status": "Completed"})
        cancelled_orders = orders_collection.count_documents({"status": "Cancelled"})

        pipeline = [
            {"$match": {"status": "Completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = list(orders_collection.aggregate(pipeline))
        total_revenue = revenue_result[0]["total"] if revenue_result else 0

        today = datetime.utcnow().date()

        today_orders = orders_collection.count_documents({
            "created_at": {
                "$gte": datetime(today.year, today.month, today.day),
                "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
            }
        })

        today_rev_pipeline = [
            {
                "$match": {
                    "status": "Completed",
                    "completed_at": {
                        "$gte": datetime(today.year, today.month, today.day),
                        "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                    }
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]

        today_rev_res = list(orders_collection.aggregate(today_rev_pipeline))
        today_revenue = today_rev_res[0]["total"] if today_rev_res else 0

        return {
            "message": "Dashboard loaded",
            "data": {
                "users": total_users,
                "restaurants": total_restaurants,
                "delivery_boys": total_delivery_boys,
                "orders": {
                    "total": total_orders,
                    "pending": pending_orders,
                    "completed": completed_orders,
                    "cancelled": cancelled_orders,
                },
                "revenue": {
                    "total_revenue": total_revenue,
                    "today_orders": today_orders,
                    "today_revenue": today_revenue,
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(dashboard_router)

# ==========================================
# Swagger Customization
# ==========================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Omkar Api Documentation",
        version="1.0.0",
        description="Swagger with JWT Bearer Auth",
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

# ============================
# New APIs: Change Password
# ============================
@app.post("/api/auth/change-password", tags=["Auth"], summary="Change Password")
def change_password(data: ChangePasswordModel, current_user: str = Depends(verify_token)):
    user = users_collection.find_one({"email": current_user})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt.checkpw(data.old_password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    new_hashed = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt())
    users_collection.update_one({"email": current_user}, {"$set": {"password": new_hashed.decode()}})
    return {"message": "Password changed successfully"}

# ============================
# Forgot Password
# ============================
@app.post("/api/auth/forgot-password", tags=["Auth"], summary="Forgot Password")
def forgot_password(data: ForgotPasswordModel):
    user = users_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    # Here, you should generate a reset token and send email; for demo, return token
    reset_token = create_access_token({"sub": data.email}, expires_delta=timedelta(hours=1))
    # Normally, send email with this token
    return {"message": "Password reset token generated", "reset_token": reset_token}

# ============================
# Reset Password
# ============================
@app.post("/api/auth/reset-password", tags=["Auth"], summary="Reset Password")
def reset_password(data: ResetPasswordModel):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_hashed = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt())
        users_collection.update_one({"email": email}, {"$set": {"password": new_hashed.decode()}})
        return {"message": "Password reset successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# ============================
# Get User Info
# ============================


@app.get("/api/auth/user-info", response_model=UserInfoResponse, tags=["Auth"], summary="Get Current User Info")
def get_user_info(current_user: str = Depends(verify_token)):
    user = users_collection.find_one({"email": current_user})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user["username"], "email": user["email"]}


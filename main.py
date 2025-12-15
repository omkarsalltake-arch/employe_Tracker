# main.py

# from fastapi import FastAPI, HTTPException, Depends, status
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

# dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# # ==========================================
# # Load environment variables
# # ==========================================
# load_dotenv()

# app = FastAPI(title="Employee Tracker API with JWT Auth")

# # ==========================================
# # MongoDB Connection
# # ==========================================
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DB = os.getenv("MONGO_DB")

# if not MONGO_URI or not MONGO_DB:
#     raise RuntimeError("MONGO_URI or MONGO_DB environment variable not set!")

# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB]
# users_collection = db["users"]

# # ==========================================
# # JWT Config
# # ==========================================
# SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_this")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
# # OAuth2 scheme (for token verification)
# # ==========================================
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# # ==========================================
# # Helper: Create JWT Token
# # ==========================================
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# # ==========================================
# # Helper: Verify JWT Token
# # ==========================================
# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if not email:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
#         return email
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")

# # ==========================================
# # Routes
# # ==========================================

# @app.get("/")
# def root():

#     return {"message": "Server is running on Render!"}



# @app.get("/db-test")
# def db_test():
#     try:
#         users_collection.find_one({})
#         return {"status": "OK"}
#     except Exception as e:
#         return {"error": str(e)}


# @app.post("/api/auth/register")
# def register_user(user: UserRegister):
#     if users_collection.find_one({"email": user.email}):
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
#     users_collection.insert_one({
#         "username": user.username,
#         "email": user.email,
#         "password": hashed_pw.decode("utf-8")
#     })
#     return {"message": "User registered successfully", "email": user.email}

# @app.post("/api/auth/login")
# def login_user(login: UserLogin):
#     user = users_collection.find_one({"email": login.email})
#     if not user or not bcrypt.checkpw(login.password.encode("utf-8"), user["password"].encode("utf-8")):
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     access_token = create_access_token(data={"sub": user["email"]})
#     return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

# @app.get("/api/protected", tags=["Protected"], summary="Protected API", description="Requires Bearer token")
# def protected_route(current_user: str = Depends(verify_token)):
#     return {"message": f"Welcome {current_user}, you have access to this protected route!"}

# @app.get("/")
# def home():
#     return {"message": "Employee Tracker API is running ..."}

# # ==========================================
# # Dashboard API
# # ==========================================

# dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# @dashboard_router.get("/", summary="Get Dashboard Analytics")
# def get_dashboard(current_user: str = Depends(verify_token)):
#     try:
#         # ============= Users Count =============
#         total_users = users_collection.count_documents({})

#         # ============= Restaurants Count =============
#         restaurants_collection = db["restaurants"]
#         total_restaurants = restaurants_collection.count_documents({})

#         # ============= Delivery Boys Count =============
#         delivery_collection = db["delivery_boys"]
#         total_delivery_boys = delivery_collection.count_documents({})

#         # ============= Orders Count =============
#         orders_collection = db["orders"]
#         total_orders = orders_collection.count_documents({})

#         pending_orders = orders_collection.count_documents({"status": "Pending"})
#         completed_orders = orders_collection.count_documents({"status": "Completed"})
#         cancelled_orders = orders_collection.count_documents({"status": "Cancelled"})

#         # ============= Revenue =============
#         pipeline_total = [
#             {"$match": {"status": "Completed"}},
#             {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
#         ]
#         total_revenue_result = list(orders_collection.aggregate(pipeline_total))
#         total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0

#         # ============= Today's Stats =============
#         today_date = datetime.utcnow().date()

#         pipeline_today_orders = [
#             {
#                 "$match": {
#                     "status": "Completed",
#                     "completed_at": {
#                         "$gte": datetime(today_date.year, today_date.month, today_date.day),
#                         "$lt": datetime(today_date.year, today_date.month, today_date.day) + timedelta(days=1)
#                     }
#                 }
#             },
#             {"$group": {"_id": None, "total_today": {"$sum": "$amount"}}}
#         ]

#         today_orders_count = orders_collection.count_documents({
#             "created_at": {
#                 "$gte": datetime(today_date.year, today_date.month, today_date.day),
#                 "$lt": datetime(today_date.year, today_date.month, today_date.day) + timedelta(days=1)
#             }
#         })

#         today_revenue_result = list(orders_collection.aggregate(pipeline_today_orders))
#         today_revenue = today_revenue_result[0]["total_today"] if today_revenue_result else 0

#         return {
#             "message": "Dashboard data fetched successfully",
#             "data": {
#                 "users": total_users,
#                 "restaurants": total_restaurants,
#                 "delivery_boys": total_delivery_boys,
#                 "orders": {
#                     "total_orders": total_orders,
#                     "pending_orders": pending_orders,
#                     "completed_orders": completed_orders,
#                     "cancelled_orders": cancelled_orders,
#                 },
#                 "revenue": {
#                     "total_revenue": total_revenue,
#                     "today_orders": today_orders_count,
#                     "today_revenue": today_revenue,
#                 }
#             }
  
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # IMPORTANT: include router BEFORE custom_openapi
# app.include_router(dashboard_router)


# # ==========================================
# # Swagger UI with BearerAuth
# # ==========================================
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema

#     openapi_schema = get_openapi(
#         title=app.title,
#         version="1.0.0",
#         description="Employee Tracker API with JWT Authentication (Swagger UI supports Bearer Token)",
#         routes=app.routes,
#     )

#     openapi_schema["components"]["securitySchemes"] = {
#         "bearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#         }
#     }

#     # Make the lock icon work
#     openapi_schema["security"] = [{"bearerAuth": []}]
    

#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

# ##  ==========================================
# ##  Run app (for local development)
# ##  ==========================================
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=port)



# date  8 december  code

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

# ==========================================
# Load .env
# ==========================================
load_dotenv()

app = FastAPI(title="Employee Tracker API with JWT Auth")

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
    return {"message": "Employee Tracker API is running ..."}

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

        restaurants = db["restaurants"]
        delivery = db["delivery_boys"]
        orders = db["orders"]

        total_restaurants = restaurants.count_documents({})
        total_delivery_boys = delivery.count_documents({})
        total_orders = orders.count_documents({})

        pending_orders = orders.count_documents({"status": "Pending"})
        completed_orders = orders.count_documents({"status": "Completed"})
        cancelled_orders = orders.count_documents({"status": "Cancelled"})

        # Revenue
        pipeline = [
            {"$match": {"status": "Completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = list(orders.aggregate(pipeline))
        total_revenue = revenue_result[0]["total"] if revenue_result else 0

        today = datetime.utcnow().date()

        today_orders = orders.count_documents({
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

        today_rev_res = list(orders.aggregate(today_rev_pipeline))
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

# Register router
app.include_router(dashboard_router)

# ==========================================
# Swagger Customization
# ==========================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Employee Tracker API with JWT",
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

# ==========================================
# Run Local
# ==========================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

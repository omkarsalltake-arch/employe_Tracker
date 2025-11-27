# Main.py

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

# ==========================================
#  Load environment variables
# ==========================================
load_dotenv()

app = FastAPI(title="Employee Tracker API with JWT Auth")

# ==========================================
#  MongoDB Connection
# ==========================================
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
users_collection = db["users"]

# ==========================================
#  JWT Config
# ==========================================
SECRET_KEY = "super_secret_key_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================================
#  Models
# ==========================================
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================================
#  OAuth2 scheme (for token verification)
# ==========================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")



# ==========================================
#  Helper: Create JWT Token
# ========================================== 
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================
#  Helper: Verify JWT Token
# ==========================================
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")


# ==========================================
#  Routes
# ==========================================
@app.post("/api/auth/register")
def register_user(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pw.decode("utf-8")
    })
    return {"message": "User registered successfully", "email": user.email}


@app.post("/api/auth/login")
def login_user(login: UserLogin):
    user = users_collection.find_one({"email": login.email})
    if not user or not bcrypt.checkpw(login.password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}


#  FIXED HERE: No `dependencies=`; use normal Depends(verify_token)
@app.get("/api/protected", tags=["Protected"], summary="Protected API", description="Requires Bearer token",)
def protected_route(current_user: str = Depends(verify_token)):
    return {"message": f"Welcome {current_user}, you have access to this protected route!"}


@app.get("/")
def home():
    return {"message": "Employee Tracker API is running ..."}
    


# ==========================================
#  Swagger UI with BearerAuth 
# ==========================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="Employee Tracker API with JWT Authentication (Swagger UI supports Bearer Token)",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    #  Important: This makes the lock icon work
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    
    return app.openapi_schema


app.openapi = custom_openapi






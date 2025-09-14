from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Manager",
    description="Internal User Management Service with Firebase",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Firebase initialization
def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Try to load from JSON file first
            firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
            if firebase_key_path and os.path.exists(firebase_key_path):
                cred = credentials.Certificate(firebase_key_path)
                logger.info("Firebase initialized from JSON file")
            else:
                # Fallback to environment variables
                private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
                if not private_key or private_key == "your-firebase-private-key":
                    logger.warning("Firebase credentials not properly configured. Using default app.")
                    firebase_admin.initialize_app()
                    return
                
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": private_key,
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                })
                logger.info("Firebase initialized from environment variables")
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        else:
            logger.info("Firebase already initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        logger.warning("Continuing without Firebase - some features may not work")
        # Don't raise the exception, just log it and continue

# Initialize Firebase on startup
initialize_firebase()

# Get Firestore client
db = firestore.client()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: Optional[bool] = None

class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: bool
    disabled: bool
    created_at: datetime
    last_sign_in: Optional[datetime] = None

@app.on_event("startup")
async def startup():
    logger.info("User Manager starting up...")

@app.on_event("shutdown")
async def shutdown():
    logger.info("User Manager shutting down...")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-manager"}

# User management endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, token: str = Depends(security)):
    """Create a new user in Firebase Auth and Firestore"""
    try:
        # Create user in Firebase Auth
        user_record = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name,
            phone_number=user_data.phone_number
        )
        
        # Store additional user data in Firestore
        user_doc = {
            "uid": user_record.uid,
            "email": user_record.email,
            "display_name": user_record.display_name,
            "phone_number": user_record.phone_number,
            "email_verified": user_record.email_verified,
            "disabled": user_record.disabled,
            "created_at": datetime.utcnow(),
            "last_sign_in": None
        }
        
        db.collection("users").document(user_record.uid).set(user_doc)
        
        logger.info(f"User created successfully: {user_record.uid}")
        
        return UserResponse(
            uid=user_record.uid,
            email=user_record.email,
            display_name=user_record.display_name,
            phone_number=user_record.phone_number,
            email_verified=user_record.email_verified,
            disabled=user_record.disabled,
            created_at=user_doc["created_at"],
            last_sign_in=user_doc["last_sign_in"]
        )
        
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, token: str = Depends(security)):
    """Get user by ID from Firestore"""
    try:
        user_doc = db.collection("users").document(user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        return UserResponse(**user_data)
        
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@app.get("/users/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, token: str = Depends(security)):
    """List all users from Firestore"""
    try:
        users_ref = db.collection("users")
        users = users_ref.offset(skip).limit(limit).stream()
        
        user_list = []
        for user_doc in users:
            user_data = user_doc.to_dict()
            user_list.append(UserResponse(**user_data))
        
        return user_list
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, token: str = Depends(security)):
    """Update user in Firebase Auth and Firestore"""
    try:
        # Update user in Firebase Auth
        update_data = {}
        if user_data.display_name is not None:
            update_data["display_name"] = user_data.display_name
        if user_data.phone_number is not None:
            update_data["phone_number"] = user_data.phone_number
        if user_data.email_verified is not None:
            update_data["email_verified"] = user_data.email_verified
        
        if update_data:
            auth.update_user(user_id, **update_data)
        
        # Update user data in Firestore
        firestore_data = {k: v for k, v in user_data.dict().items() if v is not None}
        if firestore_data:
            db.collection("users").document(user_id).update(firestore_data)
        
        # Get updated user data
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user_data = user_doc.to_dict()
        return UserResponse(**updated_user_data)
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, token: str = Depends(security)):
    """Delete user from Firebase Auth and Firestore"""
    try:
        # Delete user from Firebase Auth
        auth.delete_user(user_id)
        
        # Delete user data from Firestore
        db.collection("users").document(user_id).delete()
        
        logger.info(f"User deleted successfully: {user_id}")
        return {"message": "User deleted successfully"}
        
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

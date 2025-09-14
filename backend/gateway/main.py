from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import httpx
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="External API Gateway for microservices",
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

# Service URLs
USER_MANAGER_URL = os.getenv("USER_MANAGER_URL", "http://user-manager:8001")

# HTTP client
http_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("startup")
async def startup():
    logger.info("API Gateway starting up...")

@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()
    logger.info("API Gateway shutting down...")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

# User management endpoints
@app.post("/api/users/")
async def create_user(user_data: dict, token: str = Depends(security)):
    """Create a new user"""
    try:
        response = await http_client.post(
            f"{USER_MANAGER_URL}/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling user manager: {e}")
        raise HTTPException(status_code=503, detail="User service unavailable")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, token: str = Depends(security)):
    """Get user by ID"""
    try:
        response = await http_client.get(
            f"{USER_MANAGER_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling user manager: {e}")
        raise HTTPException(status_code=503, detail="User service unavailable")

@app.get("/api/users/")
async def list_users(skip: int = 0, limit: int = 100, token: str = Depends(security)):
    """List all users"""
    try:
        response = await http_client.get(
            f"{USER_MANAGER_URL}/users/",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling user manager: {e}")
        raise HTTPException(status_code=503, detail="User service unavailable")

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user_data: dict, token: str = Depends(security)):
    """Update user"""
    try:
        response = await http_client.put(
            f"{USER_MANAGER_URL}/users/{user_id}",
            json=user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling user manager: {e}")
        raise HTTPException(status_code=503, detail="User service unavailable")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, token: str = Depends(security)):
    """Delete user"""
    try:
        response = await http_client.delete(
            f"{USER_MANAGER_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling user manager: {e}")
        raise HTTPException(status_code=503, detail="User service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks,auth # Import routers for authentication and task operations
from app.database import engine
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.dependencies import get_current_user
from app import models  # Import models to create tables in the database


# Initialize the FastAPI app
app = FastAPI(
    title="Task Management System",
    description="A FastAPI-based task management system with real-time updates, user roles, and task assignment.",
    version="1.0.0",
    debug=True,
)

# CORS Middleware Configuration
# Adjust these settings based on your deployment environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

app.include_router(tasks.router)

# Database Table Creation
# This line will create all tables if they do not exist in the database
# models.Base.metadata.create_all(bind=engine)

@app.get("/check-token")
def check_token(user: User = Depends(get_current_user)):
    return {"message": "Token received and user authenticated", "user": user.username}

# Root Endpoint
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        test_query = db.query(User).first()  # Replace with any table in your database
        if test_query:
            return {"status": "Database connection successful!"}
        else:
            return {"status": "Connected, but no data found in User table."}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
    
@app.get("/")
async def root():
    return {"message": "Welcome to the Task Management System"}


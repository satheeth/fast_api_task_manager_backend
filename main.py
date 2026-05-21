from fastapi import FastAPI, HTTPException, status, Depends
import auth # Import our authentication module
import models # Import our models module
import task_routes # Import our tasks router
from database import engine, SessionLocal, get_db # Import engine and SessionLocal from database.py
from sqlalchemy.orm import Session
from typing import Annotated
from auth import get_current_user # Import the get_current_user dependency

app = FastAPI()
# Include the authentication router, making its endpoints available
app.include_router(auth.router)
# Include the task router
app.include_router(task_routes.router)
# Create database tables defined in models.py when the application starts
# This will create the 'users' table if it doesn't already exist
models.Base.metadata.create_all(bind=engine)
# Annotated dependencies for easy use
db_dependancy = Annotated[Session, Depends(get_db)] # Database session dependency
user_dependancy = Annotated[dict, Depends(get_current_user)] # Current authenticated user dependency
# An example protected endpoint
@app.get('/', status_code=status.HTTP_200_OK)
async def user(user: user_dependancy, db: db_dependancy):
    # The get_current_user dependency already handles authentication
    # If get_current_user raises an HTTPException, this code won't be reached.
    # So, a simple check if user is None here is redundant if get_current_user is robust.
    # We can directly use the 'user' dictionary.
    return {"message": f"Hello, {user['username']} with ID: {user['id']}!"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
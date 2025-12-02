from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Admin password (simple protection)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Define Models
class ClientSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    business_name: str
    mobile_number: str
    agreed_to_terms: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientSubmissionCreate(BaseModel):
    name: str
    business_name: str
    mobile_number: str
    agreed_to_terms: bool

class AdminLogin(BaseModel):
    password: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Client Intake API"}

@api_router.post("/submissions", response_model=ClientSubmission)
async def create_submission(input: ClientSubmissionCreate):
    if not input.agreed_to_terms:
        raise HTTPException(status_code=400, detail="You must agree to the terms and conditions")
    
    submission_dict = input.model_dump()
    submission_obj = ClientSubmission(**submission_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = submission_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.submissions.insert_one(doc)
    return submission_obj

@api_router.get("/submissions", response_model=List[ClientSubmission])
async def get_submissions():
    submissions = await db.submissions.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for submission in submissions:
        if isinstance(submission['timestamp'], str):
            submission['timestamp'] = datetime.fromisoformat(submission['timestamp'])
    
    # Sort by timestamp descending (newest first)
    submissions.sort(key=lambda x: x['timestamp'], reverse=True)
    return submissions

@api_router.post("/admin/verify")
async def verify_admin(login: AdminLogin):
    if login.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Access granted"}
    raise HTTPException(status_code=401, detail="Invalid password")

@api_router.delete("/submissions/{submission_id}")
async def delete_submission(submission_id: str):
    result = await db.submissions.delete_one({"id": submission_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"success": True, "message": "Submission deleted"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

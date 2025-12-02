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
import httpx


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

# Brevo email config
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', '')

async def send_confirmation_email(name: str, email: str, business_name: str):
    """Send professional confirmation email via Brevo"""
    if not BREVO_API_KEY or not BREVO_SENDER_EMAIL:
        logging.warning("Brevo credentials not configured, skipping email")
        return
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
            .header {{ background: linear-gradient(135deg, #FF6B35 0%, #ff8c5a 100%); padding: 40px 30px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; }}
            .header p {{ color: rgba(255,255,255,0.9); margin: 10px 0 0; font-size: 14px; }}
            .content {{ padding: 40px 30px; }}
            .greeting {{ font-size: 18px; color: #18181b; margin-bottom: 20px; }}
            .message {{ color: #52525b; line-height: 1.7; font-size: 15px; }}
            .highlight-box {{ background-color: #fff7ed; border-left: 4px solid #FF6B35; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
            .highlight-box p {{ margin: 0; color: #18181b; }}
            .details {{ background-color: #fafafa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
            .details h3 {{ margin: 0 0 15px; color: #18181b; font-size: 16px; }}
            .details p {{ margin: 5px 0; color: #52525b; font-size: 14px; }}
            .details strong {{ color: #18181b; }}
            .cta-button {{ display: inline-block; background: #FF6B35; color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background-color: #18181b; padding: 30px; text-align: center; }}
            .footer p {{ color: #a1a1aa; font-size: 13px; margin: 5px 0; }}
            .footer a {{ color: #FF6B35; text-decoration: none; }}
            .social {{ margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Nexovent Labs</h1>
                <p>Building Digital Excellence</p>
            </div>
            <div class="content">
                <p class="greeting">Dear {name},</p>
                <p class="message">
                    Thank you for reaching out to Nexovent Labs! We're thrilled to receive your inquiry and excited about the possibility of working together.
                </p>
                
                <div class="highlight-box">
                    <p><strong>What happens next?</strong><br>
                    Our team will review your submission and get back to you within <strong>7-8 hours</strong> during business days.</p>
                </div>
                
                <div class="details">
                    <h3>📋 Your Submission Details</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Business:</strong> {business_name}</p>
                    <p><strong>Submitted:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <p class="message">
                    In the meantime, feel free to explore our website to learn more about our services and past projects.
                </p>
                
                <center>
                    <a href="https://nexovent-labs.vercel.app/" class="cta-button">Visit Our Website</a>
                </center>
                
                <p class="message" style="margin-top: 30px;">
                    If you have any urgent questions, don't hesitate to reach out to us directly.
                </p>
                
                <p class="message">
                    Best regards,<br>
                    <strong>The Nexovent Labs Team</strong>
                </p>
            </div>
            <div class="footer">
                <p><strong>Nexovent Labs</strong></p>
                <p>Transforming Ideas into Digital Reality</p>
                <p style="margin-top: 15px;">
                    <a href="https://nexovent-labs.vercel.app/">Website</a>
                </p>
                <p style="margin-top: 15px; font-size: 11px; color: #71717a;">
                    © 2024 Nexovent Labs. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": BREVO_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "sender": {"name": "Nexovent Labs", "email": BREVO_SENDER_EMAIL},
                    "to": [{"email": email, "name": name}],
                    "subject": f"Welcome to Nexovent Labs, {name}! 🚀",
                    "htmlContent": html_content
                }
            )
            if response.status_code == 201:
                logging.info(f"Confirmation email sent to {email}")
            else:
                logging.error(f"Failed to send email: {response.text}")
    except Exception as e:
        logging.error(f"Email sending error: {e}")

# Define Models
class ClientSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    business_name: str
    mobile_number: str
    email: Optional[str] = None
    agreed_to_terms: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientSubmissionCreate(BaseModel):
    name: str
    business_name: str
    mobile_number: str
    email: Optional[str] = None
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
    
    # Check for duplicate entry by mobile number
    existing = await db.submissions.find_one({"mobile_number": input.mobile_number})
    if existing:
        raise HTTPException(status_code=400, detail="A submission with this mobile number already exists")
    
    # Also check by email if provided
    if input.email:
        existing_email = await db.submissions.find_one({"email": input.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="A submission with this email already exists")
    
    submission_dict = input.model_dump()
    submission_obj = ClientSubmission(**submission_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = submission_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.submissions.insert_one(doc)
    
    # Send confirmation email if email provided
    if input.email:
        await send_confirmation_email(input.name, input.email, input.business_name)
    
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

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from typing import List
from sqlalchemy.orm import Session
from email_database import SessionLocal, engine
from email_models import Base, Email
from email_schema import EmailCreate, EmailOut
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import random
import os

app = FastAPI(title="Email Simulation API")

# --- CORS (dev-friendly; ajusta si quieres restringir) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Path setup ---
_THIS_DIR = Path(__file__).resolve().parent               # server/
_EMAIL_AGENT_DIR = _THIS_DIR.parent                       # email_agent/
_STATIC_DIR = _EMAIL_AGENT_DIR / "static"
_SERVER_TEMPLATES_DIR = _THIS_DIR / "templates"

# --- Mount static files ---
if _STATIC_DIR.exists() and _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# --- Templates setup ---
# Priority: server/templates/ first, then static/ as fallback
# This allows server-specific templates to override shared ones
_TEMPLATE_SEARCH_PATHS = []
if _SERVER_TEMPLATES_DIR.exists() and _SERVER_TEMPLATES_DIR.is_dir():
    _TEMPLATE_SEARCH_PATHS.append(str(_SERVER_TEMPLATES_DIR))
if _STATIC_DIR.exists() and _STATIC_DIR.is_dir():
    _TEMPLATE_SEARCH_PATHS.append(str(_STATIC_DIR))

# Use the first available directory, or create a default
if _TEMPLATE_SEARCH_PATHS:
    from jinja2 import FileSystemLoader, Environment
    template_loader = FileSystemLoader(_TEMPLATE_SEARCH_PATHS)
    template_env = Environment(loader=template_loader)
    
    # Wrapper to maintain Jinja2Templates API compatibility
    class MultiPathTemplates:
        def __init__(self, env):
            self.env = env
        
        def TemplateResponse(self, name, context):
            template = self.env.get_template(name)
            html_content = template.render(**context)
            return HTMLResponse(content=html_content)
    
    templates = MultiPathTemplates(template_env)
else:
    # Fallback: create server/templates directory
    _SERVER_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    templates = Jinja2Templates(directory=str(_SERVER_TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Serve the email UI interface."""
    ui_email_server = os.getenv("UI_EMAIL_SERVER", "http://127.0.0.1:8000")
    ui_llm_server   = os.getenv("UI_LLM_SERVER", "http://127.0.0.1:8001")
    return templates.TemplateResponse(
        "ui_all.html",
        {"request": request, "UI_EMAIL_SERVER": ui_email_server, "UI_LLM_SERVER": ui_llm_server}
    )

# --- DB setup ---
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def preload_emails():
    db = SessionLocal()
    try:
        db.execute(delete(Email))
        db.commit()

        now = datetime.utcnow()
        samples = [
            Email(sender="boss@email.com", recipient="you@email.com",
                  subject="Quarterly Report", body="Please finalize the report ASAP.",
                  timestamp=now, read=False),
            Email(sender="alice@work.com", recipient="you@email.com",
                  subject="Lunch?", body="Free for lunch today?",
                  timestamp=now, read=False),
            Email(sender="bob@work.com", recipient="you@email.com",
                  subject="Code Review", body="I left some comments on your PR.",
                  timestamp=now, read=False),
            Email(sender="charlie@work.com", recipient="you@email.com",
                  subject="Meeting", body="Can we reschedule?",
                  timestamp=now, read=False),
            Email(sender="eric@work.com", recipient="you@email.com",
                  subject="Happy Hour", body="We're planning drinks this Friday!",
                  timestamp=now, read=False),
            Email(sender="you@mail.com", recipient="boss@email.com",
                  subject="Days off", body="Can I get some days off the coming week?",
                  timestamp=now, read=False),
        ]
        random.shuffle(samples)
        db.add_all(samples)
        db.commit()
    finally:
        db.close()

# --- API ---

@app.post("/send", response_model=EmailOut)
def send_email(email: EmailCreate, db: Session = Depends(get_db)):
    # Use provided sender or fall back to default from environment or hardcoded value
    sender_address = email.sender
    if sender_address is None:
        # Try environment variable first, then fall back to hardcoded default
        sender_address = os.getenv("USER_EMAIL", "you@mail.com")
    
    new_email = Email(
        recipient=email.recipient,
        subject=email.subject,
        body=email.body,
        sender=sender_address,
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email

@app.get("/emails", response_model=List[EmailOut])
def list_emails(db: Session = Depends(get_db)):
    return db.query(Email).order_by(Email.timestamp.desc()).all()

@app.get("/emails/search", response_model=List[EmailOut])
def search_emails(
    q: str = Query(..., description="Keyword to search in subject/body/sender"),
    db: Session = Depends(get_db),
):
    return db.query(Email).filter(
        (Email.subject.ilike(f"%{q}%")) |
        (Email.body.ilike(f"%{q}%")) |
        (Email.sender.ilike(f"%{q}%"))
    ).order_by(Email.timestamp.desc()).all()

@app.get("/emails/filter", response_model=List[EmailOut])
def filter_emails(
    recipient: str | None = Query(None, description="Recipient email address (optional)"),
    date_from: str | None = Query(None, description="Start date YYYY-MM-DD (optional)"),
    date_to: str | None = Query(None, description="End date YYYY-MM-DD (optional)"),
    db: Session = Depends(get_db),
):
    query = db.query(Email)

    if recipient:
        query = query.filter(Email.recipient == recipient)

    if date_from:
        try:
            date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Email.timestamp >= date_from_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")

    if date_to:
        try:
            date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Email.timestamp <= date_to_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")

    return query.order_by(Email.timestamp.desc()).all()

@app.get("/emails/unread", response_model=List[EmailOut])
def get_unread_emails(db: Session = Depends(get_db)):
    return db.query(Email).filter(Email.read == False).order_by(Email.timestamp.desc()).all()

@app.get("/emails/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@app.patch("/emails/{email_id}/read", response_model=EmailOut)
def mark_email_as_read(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.read = True
    db.commit()
    db.refresh(email)
    return email

@app.patch("/emails/{email_id}/unread", response_model=EmailOut)
def mark_email_as_unread(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.read = False
    db.commit()
    db.refresh(email)
    return email

@app.delete("/emails/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    db.delete(email)
    db.commit()
    return {"message": "Email deleted"}

@app.get("/reset_database")
def reset_database():
    preload_emails()
    return {"message": "Database reset and emails reloaded"}

# Salud/diagnóstico rápido
@app.get("/health")
def health():
    return {"status": "ok"}

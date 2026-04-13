from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, Lead
import uvicorn

app = FastAPI(title="Global AI Agency Dashboard")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "leads": leads,
        "total_leads": len(leads)
    })

if __name__ == "__main__":
    import os
    if not os.path.exists("templates"):
        os.makedirs("templates")
    uvicorn.run(app, host="0.0.0.0", port=8000)

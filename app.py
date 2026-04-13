from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, Lead
from maps_scraper import run_maps_scraper
import uvicorn
import csv
import io

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

    # Calculate stats here to avoid Jinja2 selectattr issues
    stats = {
        "total": len(leads),
        "hot": len([l for l in leads if l.status == "Hot Lead"]),
        "analyzed": len([l for l in leads if l.status == "Analyzed"]),
        "cities": len(set([l.city for l in leads if l.city]))
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"leads": leads, "stats": stats}
    )

@app.post("/search", response_class=HTMLResponse)
async def search_leads(request: Request, niche: str = Form(...), location: str = Form(...), db: Session = Depends(get_db)):
    # Run scraper in real-time
    run_maps_scraper(niche=niche, city=location, max_results=10)

    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    stats = {
        "total": len(leads),
        "hot": len([l for l in leads if l.status == "Hot Lead"]),
        "analyzed": len([l for l in leads if l.status == "Analyzed"]),
        "cities": len(set([l.city for l in leads if l.city]))
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"leads": leads, "stats": stats, "search_performed": True}
    )

@app.get("/export/csv")
async def export_csv(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Company", "Email", "Phone", "Website", "Niche", "City", "Status", "AI Score", "Notes", "Map Link"])

    for lead in leads:
        writer.writerow([
            lead.id, lead.name, lead.company, lead.email, lead.phone, lead.website,
            lead.niche, lead.city, lead.status, lead.ai_score, lead.notes, lead.map_link
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )

if __name__ == "__main__":
    import os
    if not os.path.exists("templates"):
        os.makedirs("templates")
    uvicorn.run(app, host="0.0.0.0", port=8000)

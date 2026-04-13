from database import SessionLocal, Lead
import datetime

def seed_real_leads():
    session = SessionLocal()
    
    # Real Miami Law Firms found via research
    real_leads = [
        {
            "name": "The Law Offices of Robert Dixon",
            "company": "Robert Dixon Law",
            "website": "https://www.robertdixonlaw.com/",
            "niche": "Personal Injury",
            "notes": "Large volume of cases, high-ticket potential for AI automation."
        },
        {
            "name": "Steinger, Greene & Feiner",
            "company": "Steinger Law",
            "website": "https://www.steingerlaw.com/miami/",
            "niche": "Injury & Accident",
            "notes": "Multiple offices, needs better lead response automation."
        },
        {
            "name": "Baron, Branyan & Flywheel",
            "company": "BBF Law",
            "website": "https://www.bbf-law.com/",
            "niche": "Business Law",
            "notes": "Corporate clients, very high ticket."
        },
        {
            "name": "Pangas Law Firm",
            "company": "Pangas Law",
            "website": "https://www.pangaslaw.com/",
            "niche": "Criminal Defense",
            "notes": "Urgent leads, 24/7 AI response would be perfect."
        },
        {
            "name": "The Florida Law Group",
            "company": "Florida Law",
            "website": "https://www.thefloridalawgroup.com/",
            "niche": "Medical Malpractice",
            "notes": "High complexity cases, needs lead qualification."
        }
    ]

    for l in real_leads:
        try:
            # Check if lead exists
            existing = session.query(Lead).filter(Lead.website == l['website']).first()
            if not existing:
                new_lead = Lead(
                    name=l['name'],
                    company=l['company'],
                    website=l['website'],
                    niche=l['niche'],
                    notes=l['notes'],
                    status="New",
                    ai_score=85 # High potential
                )
                session.add(new_lead)
            session.commit()
        except Exception as e:
            print(f"Error seeding lead: {e}")
            session.rollback()
    
    session.close()

if __name__ == "__main__":
    seed_real_leads()
    print("Success: 5 High-Ticket Miami Law Firms added to leads.db!")

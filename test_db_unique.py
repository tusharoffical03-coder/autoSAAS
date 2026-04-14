from database import SessionLocal, Lead, init_db
from sqlalchemy.exc import IntegrityError

def test_uniqueness():
    init_db()
    session = SessionLocal()

    # Clean up test data if any
    session.query(Lead).filter(Lead.phone == "1234567890").delete()
    session.commit()

    lead1 = Lead(name="Test 1", phone="1234567890", email="test1@example.com")
    session.add(lead1)
    session.commit()
    print("Lead 1 added.")

    try:
        lead2 = Lead(name="Test 2", phone="1234567890", email="test2@example.com")
        session.add(lead2)
        session.commit()
        print("FAILED: Lead 2 with same phone added.")
    except IntegrityError:
        session.rollback()
        print("SUCCESS: Lead 2 with same phone rejected.")

    try:
        lead3 = Lead(name="Test 3", phone="0987654321", email="test1@example.com")
        session.add(lead3)
        session.commit()
        print("FAILED: Lead 3 with same email added.")
    except IntegrityError:
        session.rollback()
        print("SUCCESS: Lead 3 with same email rejected.")

    # Clean up
    session.query(Lead).filter(Lead.phone == "1234567890").delete()
    session.query(Lead).filter(Lead.phone == "0987654321").delete()
    session.commit()
    session.close()

if __name__ == "__main__":
    test_uniqueness()

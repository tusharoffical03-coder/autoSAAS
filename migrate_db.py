import sqlite3

def migrate():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()

    try:
        print("Adding 'source' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'Maps'")
    except sqlite3.OperationalError:
        print("'source' column already exists.")

    try:
        print("Adding 'lead_intent' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN lead_intent TEXT DEFAULT 'Medium'")
    except sqlite3.OperationalError:
        print("'lead_intent' column already exists.")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()

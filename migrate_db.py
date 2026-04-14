import sqlite3

def migrate():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()

    try:
        print("Adding 'city' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN city TEXT")
    except sqlite3.OperationalError:
        print("'city' column already exists.")

    try:
        print("Adding 'map_link' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN map_link TEXT")
    except sqlite3.OperationalError:
        print("'map_link' column already exists.")

    try:
        print("Adding 'source' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'Maps'")
    except sqlite3.OperationalError:
        print("'source' column already exists.")

    try:
        print("Adding 'twitter' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN twitter TEXT")
    except sqlite3.OperationalError:
        print("'twitter' column already exists.")

    try:
        print("Adding 'linkedin' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN linkedin TEXT")
    except sqlite3.OperationalError:
        print("'linkedin' column already exists.")

    try:
        print("Adding 'instagram' column...")
        cursor.execute("ALTER TABLE leads ADD COLUMN instagram TEXT")
    except sqlite3.OperationalError:
        print("'instagram' column already exists.")

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

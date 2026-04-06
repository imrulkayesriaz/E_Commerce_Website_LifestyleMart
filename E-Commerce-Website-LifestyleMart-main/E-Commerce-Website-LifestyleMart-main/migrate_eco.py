"""
Migration script: Add is_eco_friendly and eco_description columns to products table.
Run this once to update the existing database without losing data.
"""
import sqlite3
import os

# Find the database file
db_path = os.path.join('instance', 'ecommerce.db')
if not os.path.exists(db_path):
    db_path = 'ecommerce.db'

if not os.path.exists(db_path):
    print("[ERROR] Database file not found. Looking in:")
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.db'):
                print(f"  Found: {os.path.join(root, f)}")
    exit(1)

print(f"[*] Using database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current columns
cursor.execute("PRAGMA table_info(products)")
columns = [row[1] for row in cursor.fetchall()]
print(f"[*] Existing columns: {columns}")

# Add is_eco_friendly if missing
if 'is_eco_friendly' not in columns:
    cursor.execute("ALTER TABLE products ADD COLUMN is_eco_friendly BOOLEAN DEFAULT 0")
    print("[OK] Added column: is_eco_friendly")
else:
    print("[SKIP] Column already exists: is_eco_friendly")

# Add eco_description if missing
if 'eco_description' not in columns:
    cursor.execute("ALTER TABLE products ADD COLUMN eco_description TEXT")
    print("[OK] Added column: eco_description")
else:
    print("[SKIP] Column already exists: eco_description")

conn.commit()
conn.close()
print("\n[SUCCESS] Migration complete! You can now run app.py")

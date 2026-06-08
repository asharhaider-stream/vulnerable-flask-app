
import sqlite3

def init_db():
    conn = sqlite3.connect("police.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suspects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            cnic TEXT,
            crime TEXT,
            status TEXT
        )
    """)
    
    suspects = [
        (1, "Syed Ashar", "35202-1234567-1", "Breaching military database", "Wanted"),
        (2, "Bilal Chaudhry", "35201-9876543-2", "20TB of CP", "Arrested"),
        (3, "Mirza Haris", "35202-1122334-3", "Drug trafficking", "Arrested"),
        (4, "Usman Tariq", "35301-4455667-4", "Vehicle theft", "Released"),
        (5, "Fahad Malik", "35202-7788990-5", "Fraud and forgery", "Arrested"),
        (6, "Zara Ahmed", "35201-1234321-6", "Money laundering", "Wanted"),
        (7, "Hassan Raza", "35202-9988776-7", "Kidnapping", "Arrested"),
        (8, "Adnan Siddiqui", "35301-5544332-8", "Cybercrime", "Wanted"),
        (9, "Tariq Mehmood", "35202-6677889-9", "Murder", "Arrested"),
        (10, "Sana Butt", "35201-3344556-0", "Embezzlement", "Released"),
        (11, "Imran Khan", "35202-8877665-1", "9 May", "Wanted"),
        (12, "Naveed Akhtar", "35301-2233445-2", "Human trafficking", "Arrested"),
        (13, "Rizwan Shah", "35202-4433221-3", "Bank fraud", "Released"),
        (14, "Faisal Qureshi", "35201-6655443-4", "Extortion", "Arrested"),
        (15, "Ayesha Noor", "35202-7766554-5", "Identity theft", "Wanted"),
        (16, "Junaid Baig", "35301-8877665-6", "Arms smuggling", "Arrested"),
        (17, "Saad Hussain", "35202-3322110-7", "Tax evasion", "Released"),
        (18, "Hamza Gill", "35201-5544337-8", "Assault", "Arrested"),
        (19, "Omar Farooq", "35202-9977556-9", "Counterfeiting", "Wanted"),
        (20, "Ijaz Sahab", "35301-1122338-0", "Illegal weapons possession", "Arrested"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO suspects VALUES (?,?,?,?,?)
    """, suspects)

    conn.commit()
    conn.close()
import sqlite3
import os
from datetime import datetime, timedelta
import random

def init_db():
    # Database file path
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', 'database.db')

    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Drop existing tables (for clean initialization)
    c.executescript('''
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS users;
    ''')

    # Create users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            ssn TEXT,
            balance REAL DEFAULT 0.0,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create transactions table
    c.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            amount REAL NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (id),
            FOREIGN KEY (to_user_id) REFERENCES users (id)
        )
    ''')

    # Insert admin user
    c.execute('''
        INSERT INTO users (username, password, email, ssn, balance, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'admin',
        'admin123',  # Insecure: Plain text password
        'admin@legacyfintech.com',
        '123-45-6789',  # Insecure: Storing SSN directly
        10000.00,
        1  # is_admin
    ))

    # Insert some test users
    test_users = [
        ('alice', 'alice123', 'alice@example.com', '111-22-3333', 5000.00, 0),
        ('bob', 'bob123', 'bob@example.com', '444-55-6666', 2500.00, 0),
        ('charlie', 'charlie123', 'charlie@example.com', '777-88-9999', 1000.00, 0),
        ('dave', 'dave123', 'dave@example.com', '000-11-2222', 750.50, 0),
        ('eve', 'eve123', 'eve@example.com', '333-44-5555', 1500.75, 0)
    ]

    c.executemany('''
        INSERT INTO users (username, password, email, ssn, balance, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', test_users)

    # Generate some random transactions
    user_ids = [1, 2, 3, 4, 5, 6]  # admin + 5 test users
    descriptions = [
        'Grocery shopping',
        'Restaurant bill',
        'Electricity bill',
        'Rent payment',
        'Online shopping',
        'Salary deposit',
        'Gift',
        'Refund',
        'Investment',
        'Withdrawal',
        'Deposit',
        'Transfer'
    ]

    # Generate 100 random transactions
    for _ in range(100):
        from_user_id = random.choice(user_ids)
        to_user_id = random.choice([uid for uid in user_ids if uid != from_user_id])
        amount = round(random.uniform(5.0, 500.0), 2)
        description = random.choice(descriptions)
        
        # Random timestamp within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        timestamp = (datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''
            INSERT INTO transactions (from_user_id, to_user_id, amount, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (from_user_id, to_user_id, amount, description, timestamp))

    # Update user balances based on transactions
    for user_id in user_ids:
        # Get the user's current balance
        c.execute('''
            SELECT balance FROM users WHERE id = ?
        ''', (user_id,))
        initial_balance = c.fetchone()['balance'] or 0.0
        
        # Calculate total received
        c.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE to_user_id = ?
        ''', (user_id,))
        received = c.fetchone()[0] or 0.0
        
        # Calculate total sent
        c.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE from_user_id = ?
        ''', (user_id,))
        sent = c.fetchone()[0] or 0.0
        
        # Calculate new balance (initial balance + received - sent)
        new_balance = initial_balance + received - sent
        
        # Update balance
        c.execute('''
            UPDATE users 
            SET balance = ? 
            WHERE id = ?
        ''', (new_balance, user_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database initialized successfully with test data!")
    print(f"Database file created at: {os.path.abspath(DB_PATH)}")
    print("\nTest Users:")
    print("-----------")
    print("Admin: admin / admin123")
    for user in test_users:
        print(f"{user[0]} / {user[1]}")
    print("\nRun the Flask app with: python api/app.py")

if __name__ == '__main__':
    init_db()

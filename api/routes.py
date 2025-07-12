from flask import Blueprint, request, jsonify, session, redirect, url_for
import sqlite3
import os
from functools import wraps
import subprocess

bp = Blueprint('api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
            
        conn = get_db_connection()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', 
                          (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or not user['is_admin']:
            return jsonify({"error": "Admin privileges required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400
    
    conn = get_db_connection()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = conn.execute(query).fetchone()
    
    if user:
        session['user_id'] = user['id']
        session['is_admin'] = bool(user['is_admin'])
        
        # Return user data (including sensitive info - bad practice!)
        user_data = dict(user)
        user_data.pop('password', None)  # Don't send password back
        
        return jsonify({
            "success": True,
            "user": user_data
        })
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@bp.route('/user/data')
@login_required
def user_data():
    conn = get_db_connection()
    
    # Get user data
    user = conn.execute('SELECT id, username, email, balance FROM users WHERE id = ?', 
                       (session['user_id'],)).fetchone()
    
    # Get recent transactions
    transactions = conn.execute('''
        SELECT t.*, 
               u1.username as from_username, 
               u2.username as to_username
        FROM transactions t
        LEFT JOIN users u1 ON t.from_user_id = u1.id
        LEFT JOIN users u2 ON t.to_user_id = u2.id
        WHERE t.from_user_id = ? OR t.to_user_id = ?
        ORDER BY t.timestamp DESC
        LIMIT 10
    ''', (session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return jsonify({
        "user": dict(user) if user else None,
        "transactions": [dict(tx) for tx in transactions]
    })

@bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    to_username = request.form.get('to_user')
    amount = request.form.get('amount')
    description = request.form.get('description', '')
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400
    
    conn = get_db_connection()
    
    try:
        # Get sender info
        sender = conn.execute('SELECT * FROM users WHERE id = ?', 
                            (session['user_id'],)).fetchone()
        
        if not sender:
            return jsonify({"error": "Sender not found"}), 404
            
        # Check balance
        if sender['balance'] < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        
        # Get recipient info - SQL Injection vulnerability
        recipient = conn.execute(f"SELECT * FROM users WHERE username = '{to_username}'").fetchone()
        
        if not recipient:
            return jsonify({"error": "Recipient not found"}), 404
            
        if recipient['id'] == sender['id']:
            return jsonify({"error": "Cannot transfer to yourself"}), 400
        
        # Perform transfer (no transaction handling!)
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', 
                   (amount, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', 
                   (amount, recipient['id']))
        
        # Log transaction - XSS vulnerability in description
        conn.execute('''
            INSERT INTO transactions (from_user_id, to_user_id, amount, description)
            VALUES (?, ?, ?, ?)
        ''', (sender['id'], recipient['id'], amount, description))
        
        conn.commit()
        
        return jsonify({"message": "Transfer successful"})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
        
    finally:
        conn.close()

@bp.route('/admin/run_command', methods=['POST'])
@admin_required
def run_command():
    command = request.form.get('command')
    if not command:
        return jsonify({"error": "No command provided"}), 400
    
    try:
        # Command injection vulnerability
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        return str(e.output), 400

@bp.route('/admin/backup', methods=['GET'])
@admin_required
def backup():
    # Insecure: No authentication in the request
    import pickle
    
    conn = get_db_connection()
    try:
        # Get all data (including sensitive info)
        users = conn.execute('SELECT * FROM users').fetchall()
        transactions = conn.execute('SELECT * FROM transactions').fetchall()
        
        # Create backup data
        backup_data = {
            'users': [dict(u) for u in users],
            'transactions': [dict(t) for t in transactions]
        }
        
        # Serialize with pickle (insecure!)
        return pickle.dumps(backup_data), 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': 'attachment; filename=backup.pkl'
        }
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@bp.route('/admin/restore', methods=['POST'])
@admin_required
def restore():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if not file.filename.endswith('.pkl'):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        # Insecure deserialization vulnerability
        import pickle
        backup_data = pickle.load(file)
        
        # Restore data (no validation!)
        conn = get_db_connection()
        
        # Clear existing data
        conn.execute('DELETE FROM transactions')
        conn.execute('DELETE FROM users')
        
        # Restore users
        for user in backup_data.get('users', []):
            conn.execute('''
                INSERT INTO users (id, username, password, email, ssn, balance, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.get('id'),
                user.get('username'),
                user.get('password'),
                user.get('email'),
                user.get('ssn'),
                user.get('balance', 0.0),
                user.get('is_admin', 0),
                user.get('created_at') or None
            ))
        
        # Restore transactions
        for tx in backup_data.get('transactions', []):
            conn.execute('''
                INSERT INTO transactions (id, from_user_id, to_user_id, amount, description, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                tx.get('id'),
                tx.get('from_user_id'),
                tx.get('to_user_id'),
                tx.get('amount'),
                tx.get('description'),
                tx.get('timestamp')
            ))
        
        conn.commit()
        return jsonify({"message": "Restore successful"})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

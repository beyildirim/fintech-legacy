from flask import Flask, send_from_directory, session
import os
from routes import bp as api_blueprint

# Initialize Flask app
app = Flask(__name__, static_folder='../web', static_url_path='')

# Configuration
app.config.update(
    SECRET_KEY='super_secret_key_123!',  # Bad practice: Hardcoded secret key
    DATABASE=os.path.join(os.path.dirname(__file__), 'database.db'),
    DEBUG=True,  # Bad practice: Debug mode in production
    TEMPLATES_AUTO_RELOAD=True  # Bad practice: Auto-reload in production
)

# Register blueprints
app.register_blueprint(api_blueprint, url_prefix='/api')

# Bad practice: Default admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def get_db_connection():
    import sqlite3
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # This will be handled by the init_db.py script
    pass

@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory(app.static_folder, 'index.html')

# Catch-all route for client-side routing
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files and handle client-side routing"""
    if path.startswith('api/'):
        # Let the API blueprint handle API routes
        return app.blueprints['api'].dispatch_request()
    
    # Try to serve the requested file
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Default to index.html for client-side routing
    return send_from_directory(app.static_folder, 'index.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html'), 200

if __name__ == '__main__':
    # Create database tables if they don't exist
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.init_db import init_db
    
    # Initialize the database
    init_db()
    
    # Run the application on port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)

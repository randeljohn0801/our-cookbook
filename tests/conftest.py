import pytest
import tempfile
import os
import sys
import atexit
from pathlib import Path
from cs50 import SQL
from flask import Flask
from flask_session import Session

# Add the parent directory to Python path so we can import the app
sys.path.append(str(Path(__file__).parent.parent))

from app import app, db

# Store database connections to close them properly
_db_connections = []

def cleanup_db_connections():
    """Clean up database connections at exit"""
    for db in _db_connections:
        try:
            db._engine.dispose()
        except:
            pass

atexit.register(cleanup_db_connections)

@pytest.fixture(autouse=True)
def app_context():
    """Create a Flask application context for the tests."""
    app.config['TESTING'] = True
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    with app.app_context():
        yield

@pytest.fixture
def client():
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    # Create a temporary file to use as our database
    db_fd, db_path = tempfile.mkstemp()
    
    # Initialize test database
    test_db = SQL(f"sqlite:///{db_path}")
    _db_connections.append(test_db)
    
    # Create tables
    test_db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    """)
    
    test_db.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipeId INTEGER PRIMARY KEY AUTOINCREMENT,
            authorId INTEGER NOT NULL,
            title TEXT NOT NULL,
            type TEXT,
            cousine TEXT,
            image TEXT,
            weight INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL
        )
    """)
    
    test_db.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            ingredientId INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId INTEGER NOT NULL,
            amount REAL NOT NULL,
            measurement TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    
    test_db.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            stepId INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId INTEGER NOT NULL,
            number INTEGER NOT NULL,
            description TEXT NOT NULL
        )
    """)
    
    # Override the app's database connection with our test database
    app.config['DATABASE'] = f'sqlite:///{db_path}'
    
    # Replace the app's database connection with our test database
    global db
    db._engine = test_db._engine
    
    yield test_db
    
    # Cleanup after tests
    try:
        test_db._engine.dispose()
        os.close(db_fd)
        os.unlink(db_path)
    except:
        pass  # Ignore cleanup errors on Windows 
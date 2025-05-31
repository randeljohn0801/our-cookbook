import pytest
from app import app, db
from flask import session

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    with app.test_client() as client:
        yield client

def test_index_get(client, test_db):
    """Test the index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Our Cookbook' in response.data  # This matches your actual title

def test_register_get(client):
    """Test the register page loads correctly"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Username' in response.data  # This should be on the register page

def test_login_get(client):
    """Test the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data  # This matches the login form field
    assert b'Password' in response.data  # This matches the login form field

def test_add_recipe_unauthorized(client):
    """Test that unauthorized users cannot access the add recipe page"""
    response = client.get('/add')
    assert response.status_code == 302  # Should redirect to login

# Helper function to login a test user
def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_login_functionality(client):
    """Test login functionality"""
    # First try with invalid credentials
    response = login(client, 'nonexistent', 'wrongpassword')
    # The response should contain either the login form again or an error message
    assert b'Username' in response.data  # Login form should be shown again
    assert b'Password' in response.data  # Login form should be shown again

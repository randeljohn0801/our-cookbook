import pytest
from account import register_user, login_user, logout_user
from flask import session, request
from werkzeug.security import generate_password_hash

@pytest.fixture
def auth_client(client, test_db):
    """Setup test database with a test user"""
    # Create a test user directly in the database
    test_db.execute(
        "INSERT INTO users (username, hash) VALUES (?, ?)",
        "testuser",
        generate_password_hash("password123")
    )
    return client

def test_register_user(auth_client):
    """Test user registration with various scenarios"""
    # Test successful registration
    response = auth_client.post('/register', data={
        'username': 'newuser',
        'password': 'password123',
        'confirmation': 'password123'
    })
    assert response.status_code == 200
    
    # Test duplicate username
    response = auth_client.post('/register', data={
        'username': 'testuser',
        'password': 'different_password',
        'confirmation': 'different_password'
    })
    assert b'error' in response.data.lower()
    
    # Test invalid input
    response = auth_client.post('/register', data={
        'username': '',
        'password': 'password123',
        'confirmation': 'password123'
    })
    assert b'error' in response.data.lower()

def test_login_user(auth_client):
    """Test user login functionality"""
    # Test successful login
    response = auth_client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200  # Should end up at home page
    
    # Test wrong password
    response = auth_client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    })
    assert b'error' in response.data.lower()
    
    # Test non-existent user
    response = auth_client.post('/login', data={
        'username': 'nonexistent',
        'password': 'password123'
    })
    assert b'error' in response.data.lower()

def test_logout_user(auth_client):
    """Test user logout"""
    # First login
    auth_client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Then test logout
    response = auth_client.get('/logout')
    assert response.status_code == 302  # Redirect to login
    
    # Check that session is cleared
    with auth_client.session_transaction() as sess:
        assert 'user_id' not in sess 
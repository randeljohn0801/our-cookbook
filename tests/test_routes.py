import pytest
from app import app, db
from datetime import datetime
from werkzeug.security import generate_password_hash
from urllib.parse import urlencode

@pytest.fixture
def auth_client(client, test_db):
    """Setup test database with a test user and recipe"""
    # Create a test user
    test_db.execute(
        "INSERT INTO users (username, hash) VALUES (?, ?)",
        "testuser",
        generate_password_hash("password123")
    )
    user_id = test_db.execute("SELECT id FROM users WHERE username = ?", "testuser")[0]['id']
    
    # Login the user
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
    
    return client, user_id

def test_basic_routes(auth_client):
    """Test basic route access"""
    client, _ = auth_client
    
    # Test home page
    response = client.get('/')
    assert response.status_code == 200
    assert b'Our Cookbook' in response.data
    
    # Test add recipe page (requires auth)
    response = client.get('/add')
    assert response.status_code == 200
    assert b'Add Recipe' in response.data

def test_recipe_workflow(auth_client, test_db):
    """Test the complete recipe workflow - add, view, edit, delete"""
    client, user_id = auth_client
    
    # 1. Add a new recipe
    form_data = {
        'title': 'Test Recipe',
        'type': 'Pasta',
        'cousine': 'Italian',
        'weight': '300',
        'ingredientAmounts[]': '200',
        'ingredientMeasurements[]': 'g',
        'ingredientDescriptions[]': 'Flour',
        'stepNumbers[]': '1',
        'stepDescriptions[]': 'Mix ingredients'
    }
    
    response = client.post('/add', data=form_data)
    assert response.status_code == 302  # Redirects to home
    
    # 2. Verify recipe was added
    recipes = test_db.execute(
        "SELECT * FROM recipes WHERE authorId = ? AND title = ?", 
        user_id, "Test Recipe"
    )
    assert len(recipes) > 0
    recipe = recipes[0]
    assert recipe['type'] == 'Pasta'
    assert recipe['weight'] == 300
    
    # 3. Check ingredients and steps
    ingredients = test_db.execute("SELECT * FROM ingredients WHERE recipeId = ?", recipe['recipeId'])
    assert len(ingredients) == 1
    assert float(ingredients[0]['amount']) == 200.0
    assert ingredients[0]['measurement'] == 'g'
    
    steps = test_db.execute("SELECT * FROM steps WHERE recipeId = ?", recipe['recipeId'])
    assert len(steps) == 1
    assert int(steps[0]['number']) == 1
    assert steps[0]['description'] == 'Mix ingredients'

def test_search_recipes(auth_client, test_db):
    """Test recipe search functionality"""
    client, user_id = auth_client
    
    # Add test recipes
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    # Add first recipe
    test_db.execute("""
        INSERT INTO recipes (authorId, title, type, cousine, weight, date, time, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, user_id, "Pasta Carbonara", "Pasta", "Italian", 400, current_date, current_time, "static/images/Default_Image.jpg")
    
    # Add second recipe
    test_db.execute("""
        INSERT INTO recipes (authorId, title, type, cousine, weight, date, time, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, user_id, "Pizza Margherita", "Pizza", "Italian", 500, current_date, current_time, "static/images/Default_Image.jpg")
    
    # Test recipe type search
    response = client.get('/?t=Recipe&q=Pasta')
    assert response.status_code == 200
    
    # Get recipes from database to verify
    recipes = test_db.execute(
        "SELECT * FROM recipes WHERE title LIKE ? AND authorId = ?",
        "%Pasta%", user_id
    )
    assert len(recipes) == 1
    assert recipes[0]['title'] == 'Pasta Carbonara'
    
    # Test recipe author search
    response = client.get('/?t=User&q=testuser')
    assert response.status_code == 200
    
    # Get recipes from database to verify
    recipes = test_db.execute(
        "SELECT r.* FROM recipes r JOIN users u ON r.authorId = u.id WHERE u.username LIKE ?",
        "%testuser%"
    )
    assert len(recipes) == 2
    titles = [r['title'] for r in recipes]
    assert 'Pizza Margherita' in titles
    assert 'Pasta Carbonara' in titles

def test_recipe_deletion(auth_client, test_db):
    """Test recipe deletion with proper authentication"""
    client, user_id = auth_client
    
    # Create a recipe
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    test_db.execute("""
        INSERT INTO recipes (authorId, title, type, cousine, weight, date, time, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, user_id, "Recipe To Delete", "Pasta", "Italian", 300, current_date, current_time, "static/images/Default_Image.jpg")
    
    recipe_id = test_db.execute(
        "SELECT recipeId FROM recipes WHERE title = ?", 
        "Recipe To Delete"
    )[0]['recipeId']
    
    # Add test ingredients and steps
    test_db.execute(
        "INSERT INTO ingredients (recipeId, amount, measurement, description) VALUES (?, ?, ?, ?)",
        recipe_id, 200, 'g', 'Test Ingredient'
    )
    test_db.execute(
        "INSERT INTO steps (recipeId, number, description) VALUES (?, ?, ?)",
        recipe_id, 1, 'Test Step'
    )
    
    # Delete the recipe
    response = client.get(f'/delete?recipeId={recipe_id}')
    assert response.status_code == 302  # Should redirect
    
    # Follow the redirect and verify deletion
    response = client.get('/')
    assert response.status_code == 200
    
    # Wait a moment for the database to update
    import time
    time.sleep(0.1)
    
    # Verify recipe and related data are deleted
    recipes = test_db.execute("SELECT * FROM recipes WHERE recipeId = ?", recipe_id)
    assert len(recipes) == 0
    
    ingredients = test_db.execute("SELECT * FROM ingredients WHERE recipeId = ?", recipe_id)
    assert len(ingredients) == 0
    
    steps = test_db.execute("SELECT * FROM steps WHERE recipeId = ?", recipe_id)
    assert len(steps) == 0

def test_authentication_requirements(auth_client):
    """Test authentication requirements for protected routes"""
    client, _ = auth_client
    
    # First test with authentication
    response = client.get('/add')
    assert response.status_code == 200
    
    # Then test without authentication
    with client.session_transaction() as sess:
        sess.clear()
    
    protected_routes = ['/add', '/edit', '/delete?recipeId=1']
    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 302  # Should redirect to login
        assert '/login' in response.headers.get('Location', '') 
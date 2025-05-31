from cs50 import SQL
from datetime import datetime

# Connect to the database
db = SQL("sqlite:///project.db")

# Get current user id (using the first user in the database for demo)
user_id = db.execute("SELECT id FROM users LIMIT 1")[0]["id"]

# Current date and time
current_date = datetime.now().date()
current_time = datetime.now().time()

# Add Chicken Adobo
adobo = db.execute("""
    INSERT INTO recipes (authorId, title, type, cousine, image, weight, date, time) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", user_id, "Chicken Adobo", "Stew", "Filipino", "static/images/adobo.jpg", 1000, current_date, current_time)

adobo_id = db.execute("SELECT recipeId FROM recipes ORDER BY recipeId DESC LIMIT 1")[0]["recipeId"]

# Adobo ingredients
adobo_ingredients = [
    (1000, "g", "Chicken Thighs"),
    (125, "ml", "Soy Sauce"),
    (125, "ml", "White Vinegar"),
    (2, "count", "Bay Leaves"),
    (8, "count", "Garlic Cloves, Crushed"),
    (1, "tbsp", "Black Peppercorns"),
    (2, "tbsp", "Cooking Oil"),
    (1, "cup", "Water")
]

for amount, measurement, description in adobo_ingredients:
    db.execute("""
        INSERT INTO ingredients (recipeId, amount, measurement, description)
        VALUES (?, ?, ?, ?)
    """, adobo_id, amount, measurement, description)

# Adobo steps
adobo_steps = [
    "In a large pot, combine chicken, soy sauce, vinegar, garlic, bay leaves, and peppercorns.",
    "Bring to a boil, then reduce heat and simmer for 30 minutes.",
    "Remove chicken from the pot and set aside.",
    "Continue boiling the sauce until reduced by half.",
    "In a large skillet, heat oil over medium-high heat.",
    "Fry the chicken pieces until browned on all sides.",
    "Pour the reduced sauce over the chicken.",
    "Simmer for additional 5-10 minutes until sauce thickens.",
    "Serve hot with steamed rice."
]

for i, step in enumerate(adobo_steps, 1):
    db.execute("""
        INSERT INTO steps (recipeId, number, description)
        VALUES (?, ?, ?)
    """, adobo_id, i, step)

# Add Sinigang
sinigang = db.execute("""
    INSERT INTO recipes (authorId, title, type, cousine, image, weight, date, time) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", user_id, "Pork Sinigang", "Soup", "Filipino", "static/images/sinigang.jpg", 1200, current_date, current_time)

sinigang_id = db.execute("SELECT recipeId FROM recipes ORDER BY recipeId DESC LIMIT 1")[0]["recipeId"]

# Sinigang ingredients
sinigang_ingredients = [
    (1000, "g", "Pork Belly, Cubed"),
    (2, "count", "Tomatoes, Quartered"),
    (1, "count", "Onion, Sliced"),
    (2, "count", "Radish, Sliced"),
    (200, "g", "String Beans"),
    (200, "g", "Spinach"),
    (2, "count", "Green Chili"),
    (44, "g", "Sinigang Mix"),
    (2, "tbsp", "Fish Sauce"),
    (8, "cup", "Water")
]

for amount, measurement, description in sinigang_ingredients:
    db.execute("""
        INSERT INTO ingredients (recipeId, amount, measurement, description)
        VALUES (?, ?, ?, ?)
    """, sinigang_id, amount, measurement, description)

# Sinigang steps
sinigang_steps = [
    "In a large pot, bring water to a boil.",
    "Add onions and tomatoes, simmer for 2-3 minutes.",
    "Add pork and cook until tender (about 30-40 minutes).",
    "Add radish and string beans, cook for 3-5 minutes.",
    "Add sinigang mix and fish sauce, stir well.",
    "Add green chili peppers.",
    "Add spinach, cook for 1 minute.",
    "Season with additional fish sauce if needed.",
    "Serve hot with steamed rice."
]

for i, step in enumerate(sinigang_steps, 1):
    db.execute("""
        INSERT INTO steps (recipeId, number, description)
        VALUES (?, ?, ?)
    """, sinigang_id, i, step)

print("Filipino recipes added successfully!") 
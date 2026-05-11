import requests
import os
import json # Added to make the printout pretty
from dotenv import load_dotenv

load_dotenv()

def fetch_food_options(food_query):
    api_key = os.getenv("USDA_API_KEY")
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food_query}&pageSize=5"
    
    response = requests.get(url)
    data = response.json()

    if not data.get('foods'):
        return []

    options = []
    for food in data['foods']:
        nutrients = food.get('foodNutrients', [])
        def get_val(id):
            return next((n['value'] for n in nutrients if n.get('nutrientId') == id), 0)

        # GATHER CONTEXT
        base_desc = food.get('description', 'Unknown').upper()
        brand = food.get('brandName') or food.get('brandOwner')
        category = food.get('foodCategory')
        
        # LOGIC: If the description is too generic, append the category or brand
        full_desc = base_desc
        if category and category.upper() not in full_desc:
            full_desc += f" ({category.upper()})"
        if brand and brand.upper() not in full_desc:
            full_desc += f" [{brand.upper()}]"

        options.append({
            "description": full_desc,
            "calories": get_val(1008),
            "protein": get_val(1003),
            "fat": get_val(1004),
            "carbs": get_val(1005),
            "fiber": get_val(1079)
        })
    return options

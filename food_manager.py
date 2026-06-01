import json

class WeeklyMealPlan:
    def __init__(self, targets):
        self.targets = targets 
        self.current_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "cost": 0}
        self.grocery_list = []
        

        self.pantry = []
        self.pantry_inventory = []

        self.price_db = self._load_price_database()

    def _load_price_database(self):
        try:
            with open('data/prices.json', 'r') as f:
                return {k.lower(): v for k, v in json.load(f).items()}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Warning: Could not load price database ({e}). Using empty dictionary.")
            return {}

    def add_to_pantry(self, food_description, servings=1):
        self.pantry.append(food_description.lower())
        self.pantry_inventory.append((food_description, servings))
    def get_price_for_item(self, api_description):
        if not self.price_db:
            return None
            
        try:
            desc_lower = api_description.lower()
            
            if desc_lower in self.price_db:
                return self.price_db[desc_lower]
            
            for item_name, price in self.price_db.items():
                if item_name in desc_lower or desc_lower in item_name:
                    return price
            
            api_words = set(desc_lower.replace(',', '').split())
            for item_name, price in self.price_db.items():
                if any(word in item_name for word in api_words if len(word) > 3):
                    return price

            return None
        except Exception as e:
            print(f"Match Error: {e}")
            return None

    def add_food(self, food_data, servings=1, force=False, is_pantry_setup=False):
        desc_lower = food_data['description'].lower()
        
        is_owned = desc_lower in self.pantry        
        if is_owned or is_pantry_setup:
            price_per_unit = 0.0
        else:
            price_per_unit = self.get_price_for_item(food_data['description'])
            if price_per_unit is None:
                price_per_unit = 0.0

        cost = price_per_unit * servings
        
        upcoming_additions = {
            "cost": cost,
            "calories": food_data['calories'] * servings,
            "protein": food_data['protein'] * servings,
            "carbs": food_data['carbs'] * servings,
            "fat": food_data['fat'] * servings,
            "fiber": food_data['fiber'] * servings
        }

        if not force:
            if (self.current_totals["cost"] + upcoming_additions["cost"]) > self.targets["cost"]:
                return "OVER_BUDGET"
            if (self.current_totals["calories"] + upcoming_additions["calories"]) > self.targets["calories"]:
                return "OVER_CALORIES"
                
            for macro in ["protein", "carbs", "fat", "fiber"]:
                if (self.current_totals[macro] + upcoming_additions[macro]) > self.targets[macro]:
                    return f"OVER_{macro.upper()}"

        self.current_totals["cost"] += cost
        
        if is_pantry_setup:
            self.pantry.append(food_data['description'].lower())
            self.pantry_inventory.append((food_data['description'], servings))
            print(f"🏠 Added {food_data['description']} to home inventory supply.")
        elif is_owned:
            print(f"🏠 Inventory Match! Using {food_data['description']} from your home supply.")
        else:
            self.grocery_list.append((food_data['description'], servings))
            print(f"✅ Added {food_data['description']} to grocery shopping list! (Cost: ${cost:.2f})")
        
        for key in ["calories", "protein", "fat", "carbs", "fiber"]:
            self.current_totals[key] += upcoming_additions[key]
        
        return True
    
    def get_remaining(self):
        return {k: self.targets[k] - self.current_totals[k] for k in self.current_totals}

import json

class WeeklyMealPlan:
    def __init__(self, targets):
        self.targets = targets # Expects {'budget': 50, 'protein': 700, etc.}
        self.current_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "cost": 0}
        self.grocery_list = []

    def get_price_for_item(self, api_description):
        try:
            with open('data/prices.json', 'r') as f:
                price_db = json.load(f)
            
            # Convert the API description to lowercase once
            desc_lower = api_description.lower()
            
            # 1. Try an exact match first
            if desc_lower in price_db:
                return price_db[desc_lower]
            
            # 2. Loop through our price database and look for partial matches
            for item_name, price in price_db.items():
                # If our price list name is inside the API description (e.g., "chicken" in "CHICKEN BREAST")
                # OR if the API name is inside our price list
                if item_name in desc_lower or desc_lower in item_name:
                    return price
            
            # 3. Last ditch effort: Check individual words
            api_words = set(desc_lower.replace(',', '').split())
            for item_name, price in price_db.items():
                if any(word in item_name for word in api_words if len(word) > 3):
                    return price

            return None
        except Exception as e:
            print(f"Match Error: {e}")
            return None
    def add_food(self, food_data, servings=1):
        # 1. Automatically find the price
        price_per_unit = self.get_price_for_item(food_data['description'])
        
        if price_per_unit is None:
            print(f"Could not find price for {food_data['description']}. Using $0.00 estimate.")
            price_per_unit = 0.0

        # Calculate impact
        cost = price_per_unit * servings
        calories_to_add = food_data['calories'] * servings

        # 2. VALIDATION GATE (Budget & Calories)
        # Check Budget
        if (self.current_totals["cost"] + cost) > self.targets["cost"]:
            print(f"❌ DENIED: Adding this exceeds your weekly budget by ${((self.current_totals['cost'] + cost) - self.targets['cost']):.2f}!!")
            return False
            
        # Check Calories (Preventing the negative)
        if (self.current_totals["calories"] + calories_to_add) > self.targets["calories"]:
            print(f"❌ DENIED: Adding this exceeds your calorie limit by {(self.current_totals['calories'] + calories_to_add - self.targets['calories']):.0f} kcal!!")
            return False

        # 3. If it passes the checks, update Totals
        self.current_totals["cost"] += cost
        self.grocery_list.append((food_data['description'], servings))
        
        for macro in ["calories", "protein", "fat", "carbs", "fiber"]:
            self.current_totals[macro] += food_data[macro] * servings
        
        print(f"✅ Added {food_data['description']}! (Cost: ${cost:.2f})")
        return True
    
    def get_remaining(self):
        # Cleaned up the dictionary comprehension syntax here
        return {k: self.targets[k] - self.current_totals[k] for k in self.current_totals}

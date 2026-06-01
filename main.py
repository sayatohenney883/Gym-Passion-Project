from api_handler import fetch_food_options
from food_manager import WeeklyMealPlan 

def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numerical value (e.g., 2500).")
            
def get_valid_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def clean_usda_name(name):
    """Cleans names while preserving the extra context we added in brackets."""
    fillers = [
        "CHICKEN, BROILER OR FRYERS, ", 
        "CHICKEN, ", 
        "PREPARED, ", 
        "RAW, ",
        "SEPARABLE LEAN AND FAT, ",
        "BONELESS, SKINLESS, "
    ]
    clean_name = name.upper()
    for word in fillers:
        if clean_name.strip() != word.strip():
            clean_name = clean_name.replace(word, "")
            
    return clean_name.strip()

def ask_to_override(warning_type):
    """Asks the user if they want to proceed despite hitting a target limit."""
    metric = warning_type.replace("OVER_", "").title()
    print(f"\n⚠️ WARNING: Adding this item will cause you to EXCEED your weekly {metric} goal!")
    
    while True:
        choice = input("Are you sure you want to add it anyway? (yes/no): ").strip().lower()
        if choice in ['yes', 'y']:
            return True
        if choice in ['no', 'n']:
            print("Action canceled. Returning to search.")
            return False
        print("Please type 'yes' or 'no'.")

def get_necessary_information():
    print("--- Set Your Weekly Goals ---")
    data = {
        "calories": get_valid_float("Enter weekly calorie goal: "),
        "protein":  get_valid_float("Enter weekly protein goal (g): "),
        "carbs":    get_valid_float("Enter weekly carb goal (g): "),
        "fat":      get_valid_float("Enter weekly fat goal (g): "),
        "fiber":    get_valid_float("Enter weekly fiber goal (g): "),
        "cost":     get_valid_float("Enter weekly budget ($): ")
    }
    return data

user_targets = get_necessary_information()

plan = WeeklyMealPlan(user_targets)

print("\n--- Check Your Kitchen Pantry ---")ˇ
print("Enter foods you ALREADY have at home. We will deduct their macros from your weekly goals.")
print("Type 'done' when you are finished updating your inventory.")

while True:
    pantry_search = input("\nWhat do you have at home? (or type 'done'): ").strip()
    if pantry_search.lower() == 'done':
        break
        
    options = fetch_food_options(pantry_search)
    
    if not options:
        print("No results found for that item. Let's try listing it differently.")
        continue

    print("\n" + "="*80)
    print(f"PANTRY MATCH FOR: {pantry_search.upper()}")
    print("Est. Market Price: $0.00 (Owned Inventory)")
    print("="*80)
    
    print(f"{'#':<3} {'DESCRIPTION':<65} {'PRO':<8} {'CAL':<8}")
    print("-" * 80)

    for i, opt in enumerate(options):
        display_name = clean_usda_name(opt['description'])
        if len(display_name) > 62:
            display_name = display_name[:62] + ".."
            
        print(f"[{i}] {display_name:<65} {opt['protein']:>5.1f}g {opt['calories']:>5.0f}k")
    
    print(f"[{len(options)}] NONE OF THESE (Search again)")
    print("-" * 80)
    
    choice = get_valid_int("Select the correct number: ")
    
    if choice == len(options):
        print("Discarding results... Let's try a different search.")
        continue

    if 0 <= choice < len(options):
        selected_pantry_food = options[choice]
        qty = get_valid_float(f"How many servings of {selected_pantry_food['description']} do you have at home? ")
        
        result = plan.add_food(selected_pantry_food, servings=qty, is_pantry_setup=True)
        
        if isinstance(result, str):
            if ask_to_override(result):
                plan.add_food(selected_pantry_food, servings=qty, force=True, is_pantry_setup=True)
                result = True
            else:
                result = False
        
        if result:
            rem = plan.get_remaining()
            
            print("\n" + "-"*40)
            print(f"{'WEEKLY REMAINING GOALS':^40}")
            print("-"*40)
            print(f"  Calories: {rem['calories']:>8.0f} kcal")
            print(f"  Protein:  {rem['protein']:>8.1f} g")
            print(f"  Carbs:    {rem['carbs']:>8.1f} g")
            print(f"  Fat:      {rem['fat']:>8.1f} g")
            print(f"  Fiber:    {rem['fiber']:>8.1f} g")
            print(f"  Budget:   ${rem['cost']:>8.2f}")
            print("-"*40)
    else:
        print("Invalid selection. Returning to pantry prompt.")

print("\n--- Moving to Grocery Shopping Loop ---")
print("\n--- Budget & Macro Tracker Initialized ---")

while True:
    food_search = input("\nEnter a food to add (or type 'done'): ").strip()
    if food_search.lower() == 'done': 
        break
        
    options = fetch_food_options(food_search)
    
    if not options:
        print("No results found.")
        continue

    general_price = plan.get_price_for_item(food_search)
    price_notice = f"Est. Market Price: ${general_price:.2f}/lb (USDA General Rate)" if general_price else "Price: Estimate Unavailable"

    print("\n" + "="*80)
    print(f"RESULTS FOR: {food_search.upper()}")
    print(f"{price_notice}")
    print("="*80)
    
    print(f"{'#':<3} {'DESCRIPTION':<65} {'PRO':<8} {'CAL':<8}")
    print("-" * 80)

    for i, opt in enumerate(options):
        display_name = clean_usda_name(opt['description'])
        if len(display_name) > 62:
            display_name = display_name[:62] + ".."
            
        print(f"[{i}] {display_name:<65} {opt['protein']:>5.1f}g {opt['calories']:>5.0f}k")
    
    print(f"[{len(options)}] NONE OF THESE (Search again)")
    print("-" * 80)
    
    choice = get_valid_int("Select the correct number: ")
    
    if choice == len(options):
        print("Discarding results... Let's try a different search.")
        continue

    if 0 <= choice < len(options):
        selected_food = options[choice]
        qty = get_valid_float(f"How many servings of {selected_food['description']}? ")
        

        result = plan.add_food(selected_food, servings=qty, is_pantry_setup=False)
        
        if isinstance(result, str):
            if ask_to_override(result):
                plan.add_food(selected_food, servings=qty, force=True, is_pantry_setup=False)
                result = True
            else:
                result = False
        
        if result:
            rem = plan.get_remaining()
            
            print("\n" + "-"*40)
            print(f"{'WEEKLY REMAINING GOALS':^40}")
            print("-"*40)
            print(f"  Calories: {rem['calories']:>8.0f} kcal")
            print(f"  Protein:  {rem['protein']:>8.1f} g")
            print(f"  Carbs:    {rem['carbs']:>8.1f} g")
            print(f"  Fat:      {rem['fat']:>8.1f} g")
            print(f"  Fiber:    {rem['fiber']:>8.1f} g")
            print(f"  Budget:   ${rem['cost']:>8.2f}")
            print("-"*40)
    else:
        print("Invalid selection. Returning to main prompt.")

print("\n" + "="*45)
print(f"{'WEEKLY MEAL PLAN SUMMARY':^45}")
print("="*45)

print("\n🏠 AT HOME INVENTORY (Used this week):")
print("-" * 45)
if not plan.pantry_inventory:
    print("  (No home inventory items utilized)")
else:
    for item, qty in plan.pantry_inventory:
        print(f"  • {item}: {qty:.1f} servings")

print("\n🛒 NEED TO PURCHASE (Grocery List):")
print("-" * 45)
if not plan.grocery_list:
    print("  (No new purchases required!)")
else:
    for item, qty in plan.grocery_list:
        print(f"  • {item}: {qty:.1f} servings")

print("\n" + "="*45)
totals = plan.current_totals
print(f"Total Protein: {totals['protein']:.1f}g / {user_targets['protein']:.1f}g")
print(f"Total Spent:   ${totals['cost']:.2f} / ${user_targets['cost']:.2f}")
print("="*45)

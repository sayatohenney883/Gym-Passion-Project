from api_handler import fetch_food_options
from food_manager import WeeklyMealPlan 

def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numerical value (e.g., 2500).")

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
        # Only replace the word if it's not the ONLY thing there
        if clean_name.strip() != word.strip():
            clean_name = clean_name.replace(word, "")
            
    return clean_name.strip()

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

# 1. Gather User Input
user_targets = get_necessary_information()

# 2. Initialize the Planner
plan = WeeklyMealPlan(user_targets)

print("\n--- Budget & Macro Tracker Initialized ---")

# 3. Simple Shopping Loop
while True:
    food_search = input("\nEnter a food to add (or type 'done'): ").strip()
    if food_search.lower() == 'done': 
        break
        
    options = fetch_food_options(food_search)
    
    if not options:
        print("No results found.")
        continue

 # --- THE SELECTION MENU ---
    # 1. Look up the price once for the general search term
    general_price = plan.get_price_for_item(food_search)
    price_notice = f"Est. Market Price: ${general_price:.2f}/lb (USDA General Rate)" if general_price else "Price: Estimate Unavailable"

    print("\n" + "="*80)
    print(f"RESULTS FOR: {food_search.upper()}")
    print(f"{price_notice}")
    print("="*80)
    
    # 2. Print a simplified table without the redundant price column
    print(f"{'#':<3} {'DESCRIPTION':<65} {'PRO':<8} {'CAL':<8}")
    print("-" * 80)

    for i, opt in enumerate(options):
        display_name = clean_usda_name(opt['description'])
        if len(display_name) > 62:
            display_name = display_name[:62] + ".."
            
        print(f"[{i}] {display_name:<65} {opt['protein']:>5.1f}g {opt['calories']:>5.0f}k")
    
    print(f"[{len(options)}] NONE OF THESE (Search again)")
    print("-" * 80)
    
    choice = int(get_valid_float("Select the correct number: "))
    
    if choice == len(options):
        print("Discarding results... Let's try a different search.")
        continue

    if 0 <= choice < len(options):
        selected_food = options[choice]
        qty = get_valid_float(f"How many servings of {selected_food['description']}? ")
        
        success = plan.add_food(selected_food, servings=qty)
        
        if success:
            rem = plan.get_remaining()
            
            # --- THE DASHBOARD ---
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

# 4. Final Summary
print("\n" + "="*30)
print("FINAL SHOPPING LIST")
print("="*30)
for item, qty in plan.grocery_list:
    print(f"- {item}: {qty} servings")

totals = plan.current_totals
print(f"\nTotal Protein: {totals['protein']}g / {user_targets['protein']}g")
print(f"Total Spent: ${totals['cost']:.2f} / ${user_targets['cost']:.2f}")

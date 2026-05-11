def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numerical value (e.g., 2500).")

def get_necessary_information():
    # Now you can get all your data in just a few lines
    data = {
        "calories": get_valid_float("Enter weekly calorie goal: "),
        "protein":  get_valid_float("Enter weekly protein goal (g): "),
        "carbs":    get_valid_float("Enter weekly carb goal (g): "),
        "fats":     get_valid_float("Enter weekly fat goal (g): "),
        "fiber":    get_valid_float("Enter weekly fiber goal (g): "),
        "budget":   get_valid_float("Enter weekly budget ($): ")
    }
    return data

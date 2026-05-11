import pandas as pd
import json
import os

def load_and_clean(filepath, food_type):
    """Generic function to clean different USDA layouts."""
    df = pd.read_csv(filepath)
    # Standardize column names by removing whitespace
    df.columns = df.columns.str.strip() 
    
    cleaned_data = {}

    if food_type in ['vegetable', 'fruit']:
        # Layouts for Veg/Fruit are identical
        # Columns: Fruit/Vegetable, Form, AverageRetailPrice
        name_col = 'Vegetable' if food_type == 'vegetable' else 'Fruit'
        
        for _, row in df.iterrows():
            # Combine name and form (e.g., "apples - fresh") for better matching
            name = f"{str(row[name_col]).lower().strip()} - {str(row['Form']).lower().strip()}"
            cleaned_data[name] = round(float(row['AverageRetailPrice']), 4)

    elif food_type == 'meat':
        # Convert Year to string and strip whitespace from Month to prevent mismatch
        df['Year'] = df['Year'].astype(str)
        df['Month'] = df['Month'].astype(str).str.strip()
            
        # Filter for the most recent data (using strings now to be safe)
        latest_meat = df[(df['Year'] == '2026') & (df['Month'] == 'March')]
            
        if latest_meat.empty:
            print("  Warning: No meat data found for March 2026. Check CSV formatting.")
            
        for _, row in latest_meat.iterrows():
            # Handle 'NA' strings or actual NaN values
            val = str(row['Value']).strip()
            if val == 'NA' or not val or pd.isna(row['Value']):
                continue
                    
            raw_name = str(row['Data_Item']).lower()
            clean_name = raw_name.replace('retail price', '').replace('"', '').strip()
                
            try:
                price_val = float(val)
                    
                # Normalize Units: Convert Cents to Dollars
                if str(row['Units']).strip() == 'Cents per pound':
                    price_val = price_val / 100
                    
                cleaned_data[clean_name] = round(price_val, 4)
            except ValueError:
                continue

    return cleaned_data

def main():
    master_price_list = {}

    # File mapping
    files_to_process = [
        ('data/raw/vegetables.csv', 'vegetable'),
        ('data/raw/fruits.csv', 'fruit'),
        ('data/raw/meats.csv', 'meat')
    ]

    for path, category in files_to_process:
        if os.path.exists(path):
            print(f"Processing {category}...")
            data = load_and_clean(path, category)
            master_price_list.update(data)
        else:
            print(f"Warning: {path} not found. Skipping.")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save final JSON
    with open('data/prices.json', 'w') as f:
        json.dump(master_price_list, f, indent=4)
        
    print(f"Success! prices.json generated with {len(master_price_list)} items.")

if __name__ == "__main__":
    main()

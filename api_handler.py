#api info
import os
from dotenv import load_dotenv

# This loads the variables from your .env file into the system environment
load_dotenv()

# Now you can access them safely
api_key = os.getenv("FOOD_API_KEY")
api_id = os.getenv("FOOD_API_ID")

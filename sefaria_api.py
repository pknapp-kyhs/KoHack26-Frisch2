# Import the requests library to fetch data from the internet
import requests
# Import the re library for searching and replacing text patterns
import re

# Function to fetch text from the Sefaria database (a free Jewish texts library)
def sefaria_api(command):
    # Build the URL to request the text from Sefaria's API
    url = f"https://www.sefaria.org/api/texts/{command}?context=0"
    # Fetch the data from the URL and convert it to a Python dictionary
    data = requests.get(url).json()
    
    # Get the English translation (empty list if it doesn't exist) 
    raw_english = data.get("text", [])
    # Get the Hebrew text (empty list if it doesn't exist)
    raw_hebrew = data.get("he", [])
    
    # If English is a list, join the items together with spaces into one paragraph
    if type(raw_english) == list:
        raw_english = " ".join(raw_english)
    
    # If Hebrew is a list, join the items together with spaces into one paragraph    
    if type(raw_hebrew) == list:
        raw_hebrew = " ".join(raw_hebrew)
    
    # Remove all HTML tags from the English text (things like <br>, <i>, <b>, etc.)
    clean_english = re.sub(r'<[^>]+>', ' ', raw_english)
    # Remove all HTML tags from the Hebrew text
    clean_hebrew = re.sub(r'<[^>]+>', ' ', raw_hebrew)
    
    # Create a formatted result string with Hebrew and English text
    results = f"Hebrew:\n{clean_hebrew}\n\nEnglish:\n{clean_english}"
    # Return the results to the caller
    return results

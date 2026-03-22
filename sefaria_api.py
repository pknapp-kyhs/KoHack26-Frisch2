import requests

while True:
    query = input("\nWhat text? (e.g., Genesis 1:1) or 'q' to quit: ")
    if query == 'q': break
    
    # 1. Fetch data and convert to JSON in one line
    data = requests.get(f"https://www.sefaria.org/api/texts/{query}?context=0&stripItags=1").json()
    
    # 2. Print the results directly 
    # (Note: Sefaria often returns the text as a Python list like ['sentence 1', 'sentence 2'])
    print("\nEnglish:", data.get("text", "Not found"))
    print("Hebrew:", data.get("he", "Not found"))
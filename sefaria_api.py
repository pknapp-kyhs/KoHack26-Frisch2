# 1. BRING IN OUR TOOLS
import requests  # This is our web browser tool. It fetches data from the internet.
import re        # 're' stands for Regular Expressions. It is a powerful search-and-destroy tool for text.

def sefaria_api(command):
    # 3. GO GET THE DATA
    # We go to Sefaria, ask for the text, and convert their response into a Python dictionary (JSON)
    url = f"https://www.sefaria.org/api/texts/{command}?context=0"
    data = requests.get(url).json()
    
    # Grab the raw English and Hebrew. 
    # (If we make a typo, it grabs an empty list [] so the program doesn't crash)
    raw_english = data.get("text", [])
    raw_hebrew = data.get("he", [])
    
    # 4. CLEANUP STEP 1: GLUE THE PIECES TOGETHER
    # Sefaria often gives us a list of sentences like: ['Sentence 1.', 'Sentence 2.']
    # We want one normal paragraph. ' '.join() takes the list and glues them together with a space.
    if type(raw_english) == list:
        raw_english = " ".join(raw_english)
        
    if type(raw_hebrew) == list:
        raw_hebrew = " ".join(raw_hebrew)
        
    # 5. CLEANUP STEP 2: THE REGEX NUKE (DESTROYING HTML)
    # This line tells the computer: 
    # "Look for a '<', find whatever is inside it, look for the closing '>', and replace that whole chunk with a blank space."
    # This instantly deletes <br>, <i>, <b>, and any other hidden website code.
    clean_english = re.sub(r'<[^>]+>', ' ', raw_english)
    clean_hebrew = re.sub(r'<[^>]+>', ' ', raw_hebrew)
    
    # 6. SHOW THE HUMAN THE RESULTS
    results = f"Hebrew:\n{clean_hebrew}\n\nEnglish:\n{clean_english}"
    return results

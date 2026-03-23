# Import the sefaria_api module to fetch texts from Sefaria
import sefaria_api
# Import regex module for searching and replacing text patterns
import re

# Helper function to split text around a specific word
def split_around_word(string, word):
    # Create a pattern that matches the word and captures it
    pattern = rf"({re.escape(word)})"
    # Split the string at that word but keep the word in the results
    return re.split(pattern, string)

# Function to combine numbers that should be together with a colon (like chapter:verse)
def join_numbers_with_colon(words):
    # Create a new list to store the results
    result = []
    # Start at the first word
    i = 0
    # Loop through all words
    while i < len(words):
        # Check if current word and next word are both digits (like "3" and "5")
        if i + 1 < len(words) and words[i].isdigit() and words[i+1].isdigit():
            # Combine them with a colon (like "3:5")
            result.append(f"{words[i]}:{words[i+1]}")
            # Skip ahead 2 words since we've processed them
            i += 2  
        else:
            # Otherwise, just add the word as-is
            result.append(words[i])
            # Move to next word
            i += 1
    # Join all words back together with spaces
    return " ".join(result)

# List of common speech recognition errors for Jewish commentary names
MISHEARD_COMMENTARIES= [
    "rossi",
    "rashid",
    "rocky",
    "russia",
    "my sector",
    "random",
    "run bomb",
    "ron bomb",
    "rom bomb",
    "rom bond",
    "run robin",
    "wrong bond",
    "run bond",
    "sephora know",
    "score now",
    "for now",
    "score know",
    "so for now",
    "bother",
    "father",
    "baba",
    "eben ezra",
    "even as or",
    "ibanez rough",
    "evan as rough"
]

# List of number words (so we can recognize "five" as a number, etc.)
NUMBER_WORDS = [
    "zero","one","two","to","too","three","four","five",
    "six","seven","eight","nine","ten",
    "eleven","twelve","thirteen","fourteen",
    "fifteen","sixteen","seventeen",
    "eighteen","nineteen",
    "twenty","thirty","forty","fifty",
    "sixty","seventy","eighty","ninety",
    "hundred","hundred","thousand","million",
    "billion","first", "second", "third", "fourth",
    "fifth", "sixth", "seventh", "eighth","ninth", 
    "tenth", "eleventh","twelfth", "thirteenth",
    "fourteenth", "fifteenth","sixteenth", "seventeenth",
    "eighteenth", "nineteenth","twentieth", "thirtieth",
    "fortieth", "fiftieth","sixtieth", "seventieth",
    "eightieth", "ninetieth","hundredth", "thousandth"]

# List of book names in Hebrew (Torah, Prophets, Writings, etc.)
BOOK_NAMES=[
    "bereshit", "shemot",
        "vayikra",
        "bamidbar",
        "devarim",
        "yehoshua",
        "shmuel alef",
        "shmuel bet",
        "melachim alef",
        "melachim bet",
        "yechezkel",
    "yeshaayahu",
    "yirmiyahu",
    "hoshea",
    "yoel",
    "amos",
    "ovadia",
    "yonah",
    "micha",
    "nachum",
    "chavakuk",
    "tzefania",
    "haggai",
    "zecharya",
    "malachi",
    "tehillim",
    "mishlei",
    "iyov",
    "shir hashirim",
    "rut",
    "eicha",
    "esther",
    "daniel",
    "ezra" ,
    "nechemia" ,
    "divrei hayamim"
]

# Function to convert English words like "ten" into the number 10
def words_to_number(text):
        # Convert to lowercase and remove hyphens
        text = text.lower().replace("-", " ")
        # Dictionary of single digit numbers
        ones = {
            "zero": 0, "oh": 0, "o": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19
        }
        # Dictionary of tens (20, 30, 40, etc.)
        tens = {
            "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60,
            "seventy": 70, "eighty": 80, "ninety": 90
        }
        # Dictionary of scales (hundred, thousand, million, etc.)
        scales = {
            "hundred": 100,
            "thousand": 1_000,
            "million": 1_000_000,
            "billion": 1_000_000_000
        }
        # Dictionary of ordinal numbers (first, second, third, etc.)
        ordinals = {
            "first": 1, "second": 2, "third": 3, "fourth": 4,
            "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
            "ninth": 9, "tenth": 10, "eleventh": 11,
            "twelfth": 12, "thirteenth": 13,
            "fourteenth": 14, "fifteenth": 15,
            "sixteenth": 16, "seventeenth": 17,
            "eighteenth": 18, "nineteenth": 19,
            "twentieth": 20, "thirtieth": 30,
            "fortieth": 40, "fiftieth": 50,
            "sixtieth": 60, "seventieth": 70,
            "eightieth": 80, "ninetieth": 90,
            "hundredth": 100, "thousandth": 1000
        }
        # Split the text into individual words
        words = text.split()
        # Track the current number being built
        current = 0
        # Track the total so far
        total = 0
        # Index for looping through words
        i = 0
        # Loop through each word
        while i < len(words):
            word = words[i]
            # Skip the word "and"
            if word == "and":
                i += 1
                continue
            # Handle compound numbers like "twenty three"
            if (
                i + 1 < len(words)
                and words[i] in ones
                and words[i + 1] in tens
            ):
                current += ones[words[i]] * 100 + tens[words[i + 1]]
                i += 2
                continue
            # If word is already a digit, add it directly
            elif word.isdigit():
                current += int(word)
            # If it's a ones digit, add it
            elif word in ones:
                current += ones[word]
            # If it's a tens digit, add it
            elif word in tens:    
                current += tens[word]
            # If it's "hundred", multiply current by 100
            elif word == "hundred":
                current *= 100
            # If it's thousand/million/billion, multiply and start fresh
            elif word in ("thousand", "million", "billion"):
                current *= scales[word]
                total += current
                current = 0
            # Handle ordinal numbers
            elif word in ordinals:
                current += ordinals[word]
            # Move to next word
            i += 1
        # Combine total and current to get the final number
        number = total + current
        return number

# Function to convert Hebrew book names to English names
def map_tanach_hebrew_to_english(hebrew):
    # Convert to lowercase
    hebrew = hebrew.lower()
    # Dictionary mapping Hebrew names to English names
    hebrew_to_english = {
        "bereshit" : "Genesis", "shemot" : "Exodus",
        "vayikra" : "Leviticus",
        "bamidbar" : "Numbers",
        "devarim" : "Deuteronomy",
        "yechezkel" : "Ezekiel",
        "yehoshua" : "Joshua",
        "shmuel alef" : "Samuel 1",
        "shmuel bet" : "Samuel 2",
        "melachim alef" : "Kings 1",   
        "melachim bet" : "Kings 2",
    "yeshaayahu" : "Isaiah",
    "yirmiyahu" : "Jeremiah",
    "hoshea" : "Hosea",
    "yoel" : "Joel",
    "amos" : "Amos",
    "ovadia" : "Obadiah",
    "yonah" : "Jonah",
    "micha" : "Micah",
    "nachum" : "Nahum",
    "chavakuk" : "Habakkuk",
    "tzefania" : "Zephaniah",
    "haggai" : "Haggai",
    "zecharya" : "Zechariah",
    "malachi" : "Malachi",
    "tehillim" : "Psalms",
    "mishlei" : "Proverbs",
    "iyov" : "Job",
    "shir hashirim" : "Song of Songs",
    "rut" : "Ruth",
    "eicha" : "Lamentations",
    "esther" : "Esther",
    "daniel" : "Daniel",
    "ezra" : "Ezra",
    "nechemia" : "Nehemiah",
    "divrei hayamim" : "Chronicles"}
    # Loop through each Hebrew name
    for i in hebrew_to_english:
        # If the Hebrew name is found in the text, replace it with English name
        if i in hebrew:
            hebrew = hebrew.replace(i, hebrew_to_english[i])
    return hebrew

# Function to remove noise from the voice input (extra words at the beginning)
def trim_noise(input_text):
    # Split the text into words
    words = input_text.split()
    # Start assuming the meaningful text begins at index 0
    meaningful_idx = 0
    # Loop through each word
    for i, word in enumerate(words):
        # Convert word to lowercase for comparison
        lower_word = word.lower()
        # Check if this word is meaningful (a book name, number, or commentary)
        if (lower_word in BOOK_NAMES or lower_word in NUMBER_WORDS or lower_word in convert_to_proper_mepharshim(word).lower()):
            # Found the first meaningful word
            meaningful_idx = i
            # Stop searching - we found the start
            break

    # Return the text starting from the first meaningful word
    return " ".join(words[meaningful_idx:])

# Function to fix common speech recognition errors for commentary names
def convert_to_proper_mepharshim(input):
    # Dictionary mapping misheard words to the correct commentary name
    commentaryAliases={
"rossi":"rashi",
"rashid":"rashi",
"rocky":"rashi",
"russia": "rashi",
"my sector": "masechta",
"random":"rambam",
"run bomb":"rambam",
"ron bomb":"rambam",
"rom bomb":"rambam",
"rom bond":"ramban",
"run robin":"ramban",
"wrong bond":"ramban",
"run bond":"ramban",
"sephora know": "seforno",
"score now": "seforno",
"for now": "seforno",
"score know": "seforno",
"so for now": "seforno",
"bother": "bava",
"father": "bava",
"baba": "bava",
"eben ezra":"ibn ezra",
"even as or":"ibn ezra",
"ibanez rough":"ibn ezra",
"evan as rough":"ibn ezra",
"eben ezra":"ibn ezra"
}
    # Loop through each misspelling
    for i in commentaryAliases:
        # If the misspelling is found in the input, replace with correct spelling
        if i in input:
            input = input.replace(i, commentaryAliases[i])
    return input

# Main function that processes voice commands and fetches the requested text
def dispatch_command(input):
        # Check if no input was provided
        if input==None:
            return "nothing was inputted"
        # Remove noise from the beginning of the input
        input=trim_noise(input)
        # Fix common speech recognition errors for commentaries
        input = convert_to_proper_mepharshim(input)
        # Convert Hebrew book names to English book names
        input = map_tanach_hebrew_to_english(input)

        # Split the input into words
        words = input.split()

        # Process each word
        for idx, word in enumerate(words):
            # If the word is a number word, convert it to a digit
            if word in NUMBER_WORDS:
                words[idx] = str(words_to_number(word))

            # Capitalize the word if it's not a digit or "on"
            if not words[idx].isdigit() and words[idx] != "on":
                words[idx] = words[idx].capitalize()
        
        # Print the processed input (for debugging)
        print(input)
        # Combine adjacent numbers with colons (like "3:5" for chapter:verse)
        cleaned_input= join_numbers_with_colon(words)
        # Try to fetch the text from Sefaria
        try:
            text=sefaria_api.sefaria_api(cleaned_input)
            # Check if we got a valid response
            if text=="Hebrew:\n\n\nEnglish:\n":
                return "Found the issue"
            return text
        except Exception as e:
            # If there's an error, print it
            print(e)
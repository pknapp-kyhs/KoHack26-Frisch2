# Hebrew and English Braille Dictionary
# Note: Hebrew Braille uses the same dots for final letters (Sofit)
braille_map = {
    # English
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 
    'y': '⠽', 'z': '⠵',
    # Hebrew
    'א': '⠁', 'ב': '⠃', 'ג': '⠛', 'ד': '⠙', 'ה': '⠓', 'ו': '⠺', 'ז': '⠵', 'ח': '⠡', 
    'ט': '⠞', 'י': '⠊', 'כ': '⠅', 'ך': '⠅', 'ל': '⠇', 'מ': '⠍', 'ם': '⠍', 'נ': '⠝', 
    'ן': '⠝', 'ס': '⠎', 'ע': '⠯', 'פ': '⠏', 'ף': '⠏', 'צ': '⠯', 'ץ': '⠯', 'ק': '⠟', 
    'ר': '⠗', 'ש': '⠮', 'ת': '⠕',
    # Common
    ' ': ' ', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖'
}

print("Braille Translator (English/Hebrew). Type 'q' to exit.")

while True:
# Prompt the user and convert input to lowercase to match dictionary keys
    text = input("\nEnter text: ").lower()

    # Exit the loop if the user types 'q'
    if text == 'q': 
        break
    
    # Translation Logic:
    # 1. Loop through every character (char) in the input string (text).
    # 2. Look up the char in 'braille_map'. If not found, keep the original char (get(char, char)).
    # 3. Join all these translated characters into one single string ("".join).
    output = "".join(braille_map.get(char, char) for char in text)

    # Display the final Braille string using an f-string for formatting
    print(f"Braille: {output}")
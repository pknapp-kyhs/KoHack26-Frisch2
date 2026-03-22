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
    text = input("\nEnter text: ").lower()
    if text == 'q': 
        break
    
    # Translation Logic
    output = "".join(braille_map.get(char, char) for char in text)
    print(f"Braille: {output}")
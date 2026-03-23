# Dictionary mapping Hebrew letters and vowels to English phonetic sounds
# This allows Hebrew text to be pronounced in English
HEBREW_PHONETIC_MAP = {
    # Hebrew consonants and their English pronunciations
    '\u05d0': '',    # Aleph (usually silent)
    '\u05d1': 'v',   # Bet (without dagesh - pronounced like "v")
    '\u05d1\u05bc': 'b', # Bet (with dagesh - pronounced like "b")
    '\u05d2': 'g',   # Gimel
    '\u05d3': 'd',   # Dalet
    '\u05d4': 'h',   # He
    '\u05d5\u05b9': 'o', # Vav + Holam (vowel "o")
    '\u05d5\u05bb': 'u', # Vav + Qubuts (vowel "u")
    '\u05d5\u05bc\u05bb': 'u', # Vav + Dagesh + Qubuts (shuruk)
    '\u05d5': 'v',   # Vav (consonant, like "v")
    '\u05d6': 'z',   # Zayin
    '\u05d7': 'ch',  # Het
    '\u05d8': 't',   # Tet
    '\u05d9': 'y',   # Yod
    '\u05da': 'ch',  # Final Kaf
    '\u05db': 'ch',  # Kaf (without dagesh)
    '\u05db\u05bc': 'k', # Kaf (with dagesh)
    '\u05dc': 'l',   # Lamed
    '\u05dd': 'm',   # Final Mem
    '\u05de': 'm',   # Mem
    '\u05de': 'm',   # Mem (duplicate)
    '\u05df': 'n',   # Final Nun
    '\u05e0': 'n',   # Nun
    '\u05e1': 's',   # Samekh
    '\u05e2': '',    # Ayin (usually silent)
    '\u05e3': 'f',   # Final Pe
    '\u05e4': 'f',   # Pe (without dagesh)
    '\u05e4\u05bc': 'p', # Pe (with dagesh)
    '\u05da\u05bc': 'k', # Final Kaf with dagesh
    '\u05e5': 'ts',  # Final Tsadi
    '\u05e6': 'ts',  # Tsadi
    '\u05e7': 'k',   # Qof
    '\u05e8': 'r',   # Resh
    '\u05e9\u05c1': 'sh', # Shin
    '\u05e9\u05c2': 's',  # Sin
    '\u05e9': 'sh',  # Shin (default)
    '\u05ea': 't',   # Tav

    # Hebrew vowel marks and their English pronunciations
    '\u05b0': 'e',   # Shva
    '\u05b1': 'e',   # Hatat Segol
    '\u05b2': 'a',   # Hatat Patach
    '\u05b3': 'o',   # Hatat Qamats
    '\u05b4': 'i',   # Hiriq
    '\u05b5': 'e',   # Tsere
    '\u05b6': 'e',   # Segol
    '\u05b7': 'a',   # Patach
    '\u05b8': 'a',   # Qamats
    '\u05b9': 'o',   # Holam
    '\u05bb': 'u',   # Qubuts
    '\u05bc': '',    # Dagesh (handled in combined letters, or silent)
    '\u05c1': '',    # Shin dot
    '\u05c2': '',    # Sin dot
}

# Function to convert Hebrew text to English phonetic sounds
def transliterate(text):
    """
    Translates Hebrew text to English phonetic sounds using the dictionary.
    Note: This is a simplified transliterator.
    """
    # If empty string is passed, return None
    if text=="":
        return None
    
    # Replace the special name for God with "Hashem"
    text=text.replace('\u05d9\u05d4\u05d5\u05d4', "Hashem")
    
    # Helper function to sort keys by length using merge sort
    # This ensures longer keys are matched first (important for combined letters)
    def merge_sort(keys):
        # Base case: if list has 1 or fewer items, it's already sorted
        """Sort keys so combinations come before single characters."""
        if len(keys) <= 1:
            return keys
        
        # Find the middle point
        mid = len(keys) // 2
        # Recursively sort the left half
        left = merge_sort(keys[:mid])
        # Recursively sort the right half
        right = merge_sort(keys[mid:])
        
        # Merge the two sorted halves
        result = []
        i = j = 0
        # Compare items from left and right, adding larger keys first
        while i < len(left) and j < len(right):
            if len(left[i]) >= len(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        # Add any remaining items from left
        result.extend(left[i:])
        # Add any remaining items from right
        result.extend(right[j:])
        return result
    
    # Sort the Hebrew keys by length (longest first)
    sorted_keys = merge_sort(list(HEBREW_PHONETIC_MAP.keys()))
    
    # String to hold the result
    result = ""
    # Index for looping through the Hebrew text
    i = 0
    # Loop through each character in the text
    while i < len(text):
        # Track whether we found a matching Hebrew character
        match_found = False
        # Try to match each key (Hebrew character pattern) starting from longest
        for key in sorted_keys:
            # Check if the current position matches this Hebrew pattern
            if text.startswith(key, i):
                # Add the corresponding English sound to the result
                result += HEBREW_PHONETIC_MAP[key]
                # Skip ahead by the length of the matched pattern
                i += len(key)
                # Mark that we found a match
                match_found = True
                # Stop looking for more matches at this position
                break
        
        # If no Hebrew pattern matched, keep the character as-is
        if not match_found:
            # Add the non-Hebrew character (like punctuation or numbers)
            result += text[i]
            # Move to next character
            i += 1
        
    return result

# Test the transliterator if this file is run directly
if __name__ == "__main__":
    # Test word 1: Shalom (peace)
    test_word = "שָׁלוֹם"
    print(f"Hebrew: {test_word}")
    print(f"Transliterated: {transliterate(test_word)}")
    
    # Test word 2: Israel
    test_word_2 = "יִשְׂרָאֵל"
    print(f"Hebrew: {test_word_2}")
    print(f"Transliterated: {transliterate(test_word_2)}")

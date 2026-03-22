# Hebrew to English Transliteration Dictionary
# This dictionary maps Hebrew letters and Niqqud (vowels) to their English phonetic sounds.

HEBREW_PHONETIC_MAP = {
    # Letters
    '\u05d0': '',    # Aleph (often silent)
    '\u05d1': 'v',   # Bet (without dagesh)
    '\u05d1\u05bc': 'b', # Bet (with dagesh)
    '\u05d2': 'g',   # Gimel
    '\u05d3': 'd',   # Dalet
    '\u05d4': 'h',   # He
    '\u05d5': 'v',   # Vav
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
    '\u05de': 'm',   # Mem
    '\u05df': 'n',   # Final Nun
    '\u05e0': 'n',   # Nun
    '\u05e1': 's',   # Samekh
    '\u05e2': '',    # Ayin (often silent)
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

    # Niqqud (Vowels)
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
    '\u05bc': '',    # Dagesh (handled in combined letters above, or silent)
    '\u05c1': '',    # Shin dot
    '\u05c2': '',    # Sin dot
}

def transliterate(text):
    """
    Translates Hebrew text to English phonetic sounds using the dictionary.
    Note: This is a simplified transliterator.
    """
    # Sort keys by length descending to match combined characters (like Shin + dot) first
    sorted_keys = sorted(HEBREW_PHONETIC_MAP.keys(), key=len, reverse=True)
    
    result = ""
    i = 0
    while i < len(text):
        match_found = False
        for key in sorted_keys:
            if text.startswith(key, i):
                result += HEBREW_PHONETIC_MAP[key]
                i += len(key)
                match_found = True
                break
        if not match_found:
            result += text[i] # Keep non-Hebrew characters as is
            i += 1
    return result

# Example Usage:
if __name__ == "__main__":
    test_word = "שָׁלוֹם" # Shalom
    print(f"Hebrew: {test_word}")
    print(f"Transliterated: {transliterate(test_word)}")
    test_word_2 = "יִשְׂרָאֵל" # Israel
    print(f"Hebrew: {test_word_2}")
    print(f"Transliterated: {transliterate(test_word_2)}")
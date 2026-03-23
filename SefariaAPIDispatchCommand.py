import re

import sefaria_api


def split_around_word(string, word):
    """Split the string around the specified word while preserving the delimiter."""
    pattern = rf"({re.escape(word)})"
    return re.split(pattern, string)


def join_numbers_with_colon(words):
    """When two digits appear consecutively, join them using a colon for Sefaria parsing."""
    result = []
    i = 0
    while i < len(words):
        if i + 1 < len(words) and words[i].isdigit() and words[i + 1].isdigit():
            result.append(f"{words[i]}:{words[i+1]}")
            i += 2
        else:
            result.append(words[i])
            i += 1
    return " ".join(result)


# Common misheard phrases that should resolve to specific commentators in future abstractions.
MISHEARD_COMMENTARIES = [
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
    "evan as rough",
]


# Words that represent numbers so we can normalize Hancock-style voice input.
NUMBER_WORDS = [
    "zero",
    "one",
    "two",
    "to",
    "too",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
    "hundred",
    "hundred",
    "thousand",
    "million",
    "billion",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
    "twentieth",
    "thirtieth",
    "fortieth",
    "fiftieth",
    "sixtieth",
    "seventieth",
    "eightieth",
    "ninetieth",
    "hundredth",
    "thousandth",
]


# Books of Tanach that anchor the transcript when triggered by a voice command.
BOOK_NAMES = [
    "bereshit",
    "shemot",
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
    "ezra",
    "nechemia",
    "divrei hayamim",
]


def words_to_number(text):
    """Convert spoken English numbers into their numerical values."""
    normalized = text.lower().replace("-", " ")
    ones = {
        "zero": 0,
        "oh": 0,
        "o": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
    }
    tens = {
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }
    scales = {
        "hundred": 100,
        "thousand": 1_000,
        "million": 1_000_000,
        "billion": 1_000_000_000,
    }
    ordinals = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
        "tenth": 10,
        "eleventh": 11,
        "twelfth": 12,
        "thirteenth": 13,
        "fourteenth": 14,
        "fifteenth": 15,
        "sixteenth": 16,
        "seventeenth": 17,
        "eighteenth": 18,
        "nineteenth": 19,
        "twentieth": 20,
        "thirtieth": 30,
        "fortieth": 40,
        "fiftieth": 50,
        "sixtieth": 60,
        "seventieth": 70,
        "eightieth": 80,
        "ninetieth": 90,
        "hundredth": 100,
        "thousandth": 1_000,
    }

    words = normalized.split()
    current = 0
    total = 0
    i = 0
    while i < len(words):
        word = words[i]
        if word == "and":
            i += 1
            continue
        if (
            i + 1 < len(words)
            and words[i] in ones
            and words[i + 1] in tens
        ):
            current += ones[words[i]] * 100 + tens[words[i + 1]]
            i += 2
            continue
        if word.isdigit():
            current += int(word)
        elif word in ones:
            current += ones[word]
        elif word in tens:
            current += tens[word]
        elif word == "hundred":
            current *= 100
        elif word in ("thousand", "million", "billion"):
            current *= scales[word]
            total += current
            current = 0
        elif word in ordinals:
            current += ordinals[word]
        i += 1
    return total + current


def map_tanach_hebrew_to_english(hebrew):
    """Replace transliterated Tanach names with their English counterparts."""
    hebrew = hebrew.lower()
    hebrew_to_english = {
        "bereshit": "Genesis",
        "shemot": "Exodus",
        "vayikra": "Leviticus",
        "bamidbar": "Numbers",
        "devarim": "Deuteronomy",
        "yechezkel": "Ezekiel",
        "yehoshua": "Joshua",
        "shmuel alef": "Samuel 1",
        "shmuel bet": "Samuel 2",
        "melachim alef": "Kings 1",
        "melachim bet": "Kings 2",
        "yeshaayahu": "Isaiah",
        "yirmiyahu": "Jeremiah",
        "hoshea": "Hosea",
        "yoel": "Joel",
        "amos": "Amos",
        "ovadia": "Obadiah",
        "yonah": "Jonah",
        "micha": "Micah",
        "nachum": "Nahum",
        "chavakuk": "Habakkuk",
        "tzefania": "Zephaniah",
        "haggai": "Haggai",
        "zecharya": "Zechariah",
        "malachi": "Malachi",
        "tehillim": "Psalms",
        "mishlei": "Proverbs",
        "iyov": "Job",
        "shir hashirim": "Song of Songs",
        "rut": "Ruth",
        "eicha": "Lamentations",
        "esther": "Esther",
        "daniel": "Daniel",
        "ezra": "Ezra",
        "nechemia": "Nehemiah",
        "divrei hayamim": "Chronicles",
    }
    for key in hebrew_to_english:
        if key in hebrew:
            hebrew = hebrew.replace(key, hebrew_to_english[key])
    return hebrew


def trim_noise(input_text):
    """Drop any leading filler words until the first meaningful section name appears."""
    words = input_text.split()
    meaningful_idx = 0
    for i, word in enumerate(words):
        lower_word = word.lower()
        if (
            lower_word in BOOK_NAMES
            or lower_word in NUMBER_WORDS
            or lower_word in convert_to_proper_mepharshim(word).lower()
        ):
            meaningful_idx = i
            break
    return " ".join(words[meaningful_idx:])


def convert_to_proper_mepharshim(input_text):
    """Substitute misheard commentator names with their canonical versions."""
    commentary_aliases = {
        "rossi": "rashi",
        "rashid": "rashi",
        "rocky": "rashi",
        "russia": "rashi",
        "my sector": "masechta",
        "random": "rambam",
        "run bomb": "rambam",
        "ron bomb": "rambam",
        "rom bomb": "rambam",
        "rom bond": "ramban",
        "run robin": "ramban",
        "wrong bond": "ramban",
        "run bond": "ramban",
        "sephora know": "seforno",
        "score now": "seforno",
        "for now": "seforno",
        "score know": "seforno",
        "so for now": "seforno",
        "bother": "bava",
        "father": "bava",
        "baba": "bava",
        "eben ezra": "ibn ezra",
        "even as or": "ibn ezra",
        "ibanez rough": "ibn ezra",
        "evan as rough": "ibn ezra",
    }
    normalized = input_text.lower()
    for alias, replacement in commentary_aliases.items():
        if alias in normalized:
            normalized = normalized.replace(alias, replacement)
    return normalized


def dispatch_command(input_text):
    """Normalize a spoken query and fetch the requested text from the Sefaria API."""
    if input_text is None:
        return "nothing was inputted"

    normalized = trim_noise(input_text)
    normalized = convert_to_proper_mepharshim(normalized)
    normalized = map_tanach_hebrew_to_english(normalized)

    words = normalized.split()
    for idx, word in enumerate(words):
        if word in NUMBER_WORDS:
            words[idx] = str(words_to_number(word))
        if not words[idx].isdigit() and words[idx] != "on":
            words[idx] = words[idx].capitalize()

    cleaned_input = join_numbers_with_colon(words)
    print(normalized)
    try:
        text = sefaria_api.sefaria_api(cleaned_input)
        if text == "Hebrew:\n\n\nEnglish:\n":
            return "Found the issue"
        return text
    except Exception as error:
        print(error)

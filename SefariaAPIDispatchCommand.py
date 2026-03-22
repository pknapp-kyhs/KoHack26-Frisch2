import sefaria_api
import re
def split_around_word(string, word):
    pattern = rf"({re.escape(word)})"
    return re.split(pattern, string)
def join_numbers_with_colon(words):
    result = []
    i = 0
    while i < len(words):
        if i + 1 < len(words) and words[i].isdigit() and words[i+1].isdigit():
            result.append(f"{words[i]}:{words[i+1]}")
            i += 2  
        else:
            result.append(words[i])
            i += 1
    return " ".join(result)
NUMBER_WORDS = [
    "zero","one","two","three","four","five",
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
def words_to_number(text):
        text = text.lower().replace("-", " ")
        ones = {
            "zero": 0, "oh": 0, "o": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19
        }
        tens = {
            "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60,
            "seventy": 70, "eighty": 80, "ninety": 90
        }
        scales = {
            "hundred": 100,
            "thousand": 1_000,
            "million": 1_000_000,
            "billion": 1_000_000_000
        }
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
        words = text.split()
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
            elif word.isdigit():
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
        number = total + current
        return number
def map_tanach_hebrew_to_english(hebrew):
    hebrew = hebrew.lower()
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
    for i in hebrew_to_english:
        if i in hebrew:
            hebrew = hebrew.replace(i, hebrew_to_english[i])
    return hebrew
def dispatch_command(input):
    words = input.split()
    for idx, word in enumerate(words):
        if word in NUMBER_WORDS:
            words[idx] = str(words_to_number(word))
        elif word in BOOK_NAMES:
            words[idx]=str(map_tanach_hebrew_to_english(word))
    cleaned_input= join_numbers_with_colon(words)
    return sefaria_api.sefaria_api(cleaned_input)
print(dispatch_command("Rashi on bereshit one one"))

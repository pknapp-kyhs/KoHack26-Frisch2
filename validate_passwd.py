# Password validation function - makes sure passwords are strong and secure
def validate_passwd(password):
    # Track whether the password meets each requirement
    has_chars = False  # Will be True if password has 8+ characters
    has_special = False  # Will be True if password has a special character like ! or #
    has_upper = False  # Will be True if password has at least one capital letter
    has_lower = False  # Will be True if password has at least one lowercase letter

    # List of special characters that count as "special"
    special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "}", "{", "[", "]", "?", "/"]

    # Check if password is at least 8 characters long
    if len(password) >= 8:
        has_chars = True

    # Loop through each letter in the password to check what types of characters it has
    for letter in password:
        if letter in special_chars:  # Does it contain a special character?
            has_special = True
        if letter.isupper():  # Does it contain an uppercase letter?
            has_upper = True
        if letter.islower():  # Does it contain a lowercase letter?
            has_lower = True

    # Only return True if ALL four requirements are met
    if has_chars and has_lower and has_upper and has_special:
        return True  # Password is strong - accept it
    else:
        return False  # Password is weak - reject it
        

def validate_passwd(password):
    """Ensure the password is long enough and includes upper/lower/special characters."""
    has_chars = False
    has_special = False
    has_upper = False
    has_lower = False

    special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "}", "{", "[", "]", "?", "/"]

    if len(password) >= 8:
        has_chars = True

    for letter in password:
        # Track the presence of a special character, uppercase, and lowercase letters.
        if letter in special_chars:
            has_special = True
        if letter.isupper():
            has_upper = True
        if letter.islower():
            has_lower = True

    # Return True only when all requirements are met.
    if has_chars and has_lower and has_upper and has_special:
        return True
    return False
        

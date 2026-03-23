def validate_passwd(password):
    has_chars = False
    has_special = False
    has_upper = False
    has_lower = False

    special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "}", "{", "[", "]", "?", "/"]

    if len(password) >= 8:
        has_chars = True

    for letter in password:
        if letter in special_chars:
            has_special = True
        if letter.isupper():
            has_upper = True
        if letter.islower():
            has_lower = True

    if has_chars and has_lower and has_upper and has_special:
        return True
    else:
        return False
        

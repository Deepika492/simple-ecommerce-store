import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils.translation import gettext as _

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
)

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')

def validate_email_address(email):
    """
    Validates email format strictly.
    Rejects:
    - deepika@gmail
    - deepika@
    - @gmail.com
    - deepika gmail.com
    - deepika@gmail.
    - deepika..test@gmail.com
    """
    if not email or not isinstance(email, str):
        raise ValidationError(_("Please enter a valid email address."))
    
    email = email.strip()
    
    # Disallow empty, spaces, or consecutive dots
    if not email or ' ' in email or '..' in email:
        raise ValidationError(_("Please enter a valid email address."))
        
    # Check regex format
    if not EMAIL_REGEX.match(email):
        raise ValidationError(_("Please enter a valid email address."))
    
    # Run Django standard email validator for additional safety
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError(_("Please enter a valid email address."))
        
    return email

def validate_username_string(username):
    """
    Validates username:
    - Required
    - 3 to 30 characters
    - Letters, numbers, and underscores only
    - No spaces
    """
    if not username or not isinstance(username, str):
        raise ValidationError(_("Username is required."))
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError(_("Username must be at least 3 characters long."))
    
    if len(username) > 30:
        raise ValidationError(_("Username cannot exceed 30 characters."))
        
    if ' ' in username:
        raise ValidationError(_("Username cannot contain spaces."))
        
    if not USERNAME_REGEX.match(username):
        raise ValidationError(_("Username can only contain letters, numbers, and underscores."))
        
    return username

def validate_password_strength(password, username=None, email=None):
    """
    Validates password against all required security rules:
    1. Minimum 8 characters
    2. At least one uppercase letter (A-Z)
    3. At least one lowercase letter (a-z)
    4. At least one number (0-9)
    5. At least one special character (@#$%!^&*_- and other standard symbols)
    6. No spaces
    7. Not purely numeric
    8. Not identical / overly similar to username or email
    """
    if not password or not isinstance(password, str):
        raise ValidationError(_("Password is required."))
    
    if len(password) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))
        
    if ' ' in password:
        raise ValidationError(_("Password cannot contain spaces."))
        
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_("Password must contain at least one uppercase letter (A-Z)."))
        
    if not re.search(r'[a-z]', password):
        raise ValidationError(_("Password must contain at least one lowercase letter (a-z)."))
        
    if not re.search(r'[0-9]', password):
        raise ValidationError(_("Password must contain at least one number (0-9)."))
        
    if not re.search(r'[@#$%!^&*_\-+=()[\]{};:\'",.<>?/\\|`~]', password):
        raise ValidationError(_("Password must contain at least one special character (e.g. @, #, $, %, !, ^, &, *, _, -)."))
        
    if password.isdigit():
        raise ValidationError(_("Password cannot be entirely numeric."))
        
    if username and password.lower() == username.lower():
        raise ValidationError(_("Password cannot be identical to your username."))
        
    if email:
        email_clean = email.strip().lower()
        prefix = email_clean.split('@')[0]
        if password.lower() == email_clean or password.lower() == prefix:
            raise ValidationError(_("Password cannot be identical to your email."))
        
    return password

class CustomPasswordComplexityValidator:
    """
    Django standard password validator plugin for AUTH_PASSWORD_VALIDATORS.
    """
    def validate(self, password, user=None):
        username = user.username if user else None
        email = user.email if user else None
        validate_password_strength(password, username=username, email=email)

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, one uppercase letter, "
            "one lowercase letter, one number, one special character, and no spaces."
        )

import re

PHONE_RE = re.compile(r"^\+?\d{10,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    pass


def require_fields(data: dict, fields: list[str]):
    missing = [f for f in fields if not str(data.get(f, "")).strip()]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_phone(phone: str):
    if not PHONE_RE.match(phone.strip()):
        raise ValidationError("Enter a valid phone number (10-15 digits).")


def validate_email(email: str):
    if email and not EMAIL_RE.match(email.strip()):
        raise ValidationError("Enter a valid email address.")


def validate_positive_number(value, field_name="value"):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number.")
    if number < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    return number

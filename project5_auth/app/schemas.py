import re

from marshmallow import Schema, fields, validate, validates, ValidationError

PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, load_only=True)

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not PASSWORD_RE.match(value):
            raise ValidationError(
                "Password must be 8+ chars and include an uppercase letter, "
                "lowercase letter, digit, and special character."
            )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class RefreshSchema(Schema):
    refresh_token = fields.Str(required=True)

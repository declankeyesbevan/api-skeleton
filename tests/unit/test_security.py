from app.security import PasswordValidator


def test_password_validator():
    no_upper = {'foobarjonesiscool1!': 'upper-case'}
    no_lower = {'FOOBARJONESISCOOL1!': 'lower-case'}
    no_number = {'Foobarjonesiscool!': 'number'}
    no_special = {'Foobarjonesiscool1': 'special'}
    for combo in [no_upper, no_lower, no_number, no_special]:
        for password, error in combo.items():
            password_invalid = PasswordValidator().validate_password(password)
            assert any(error in s for s in password_invalid)

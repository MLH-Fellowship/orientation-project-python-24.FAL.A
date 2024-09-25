"""
Helper functions for the Flask application
"""

import phonenumbers


def validate_fields(field_names, request_data):
    """
    Checks that the required fields are in the request data
    """
    return [
        field
        for field in field_names
        if field not in request_data or request_data[field] in [None, "", "null"]
    ]


def validate_phone_number(phone_number):
    """
    Checks that the phone number is valid and properly internationalized
    """
    try:
        if phone_number and phone_number.startswith("+"):
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        return False
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

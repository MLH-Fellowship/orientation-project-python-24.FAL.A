'''
Helper functions for the Flask application
'''
import phonenumbers


def validate_fields(field_names, request_data):
    """
    Checks that the required fields are in the request data.
    
    :param field_names: A list of field names to validate.
    :param request_data: The data dictionary in which the fields should be checked.
        
    :return: A list of missing or invalid fields.
    """
    return [field for field in field_names
            if field not in request_data or request_data[field] in [None, '', 'null']]


def validate_phone_number(phone_number):
    """
    Checks that the phone number is valid and properly internationalized.
    
    :param phone_number: The phone number to validate, expected in international format
    (starting with '+').
    
    :return: True if the phone number is valid, False otherwise.
    """
    try:
        if phone_number and phone_number.startswith('+'):
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        return False
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

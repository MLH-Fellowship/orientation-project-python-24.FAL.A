
def validate_fields(field_names, request_data):
    '''
    Checks that the required fields are in the request data
    '''
    return [field for field in field_names
            if field not in request_data or request_data[field] in [None, '', 'null']]

'''
Helper functions for the Flask application
'''
import json
import phonenumbers
from models import Experience, Education, Skill, UserInformation


def validate_fields(field_names, request_data):
    '''
    Checks that the required fields are in the request data
    '''
    return [field for field in field_names
            if field not in request_data or request_data[field] in [None, '', 'null']]


def validate_phone_number(phone_number):
    '''
    Checks that the phone number is valid and properly internationalized
    '''
    try:
        if phone_number and phone_number.startswith('+'):
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        return False
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    

def load_data(filename):
    """
    Using dataclasses to serialize and deserialize JSON data.
    this forms a "layer" between the data and the application.
    Saving and loading data from a JSON file
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return {
            "experience": [Experience(**exp) for exp in data.get('experience', [])], 
            "education": [Education(**edu) for edu in data.get('education', [])],
            "skill": [Skill(**skl) for skl in data.get('skill', [])],
            "user_information": [UserInformation(**info) for info in data.get('user_information', [])]
        }
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return {"experience": [], "education": [], "skill": [], "user_information": []}  
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {"experience": [], "education": [], "skill": [], "user_information": []}
    
def save_data(filename, data):
    """
    This function writes the data to a JSON file. 
    First it converts the data to a dictionary, then writes it to the file.
    """
    try:
        with open(filename, 'w') as file:
            json_data = {
                "experience": [exp.__dict__ for exp in data['experience']],
                "education": [edu.__dict__ for edu in data['education']],
                "skill": [skl.__dict__ for skl in data['skill']],
                "user_information": [info.__dict__ for info in data['user_information']]
            }
            json.dump(json_data, file, indent=4)
    except IOError as e:
        print(f"An error occurred while writing to {filename}: {e}")

def generate_id(data, model):
    """
    Generate a new ID for a model
    """
    if data[model]:
        return max(item.id for item in data[model] if item.id is not None) + 1
    return 1

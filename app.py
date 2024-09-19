'''
Flask Application
'''
from flask import Flask, jsonify, request
from models import Experience, Education, Skill
from helpers import validate_fields, validate_phone_number

app = Flask(__name__)

data = {
    "experience": [
        Experience("Software Developer",
                   "A Cool Company",
                   "October 2022",
                   "Present",
                   "Writing Python Code",
                   "example-logo.png")
    ],
    "education": [
        Education("Computer Science",
                  "University of Tech",
                  "September 2019",
                  "July 2022",
                  "80%",
                  "example-logo.png")
    ],
    "skill": [
        Skill("Python",
              "1-2 Years",
              "example-logo.png")
    ],
    "user_information":
        {
            "name": "",
            "email_address": "",
            "phone_number": ""
    }
}


@app.route('/', strict_slashes=False)
def index():
    '''
    Returns a welcome message for the app
    '''
    return "Welcome to MLH 24.FAL.A.2 Orientation API Project!!"

@app.route('/test')
def hello_world():
    '''
    Returns a JSON test message
    '''
    return jsonify({"message": "Hello, World!"})

def test_index(client):
    """Test the index route"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Welcome to MLH 24.FAL.A.2 Orientation API Project!!"

@app.route('/resume/experience', methods=['GET', 'POST'])
def experience():
    '''
    Handle experience requests
    '''
    if request.method == 'GET':
        experience_list = [exp.__dict__ for exp in data['experience']]
        return jsonify(experience_list), 200

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        request_body = request.get_json()

        required_fields = {
            'title': str,
            'company': str,
            'start_date': str,
            'end_date': str,
            'description': str,
            'logo': str
        }

        missing_fields = []
        invalid_fields = []

        for field, field_type in required_fields.items():
            if field not in request_body:
                missing_fields.append(field)
            elif not isinstance(request_body[field], field_type):
                invalid_fields.append(field)

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        if invalid_fields:
            return jsonify({
                'error': 'Invalid field types',
                'invalid_fields': invalid_fields
            }), 400
        new_experience = Experience(
            request_body['title'],
            request_body['company'],
            request_body['start_date'],
            request_body['end_date'],
            request_body['description'],
            request_body['logo']
        )
        data['experience'].append(new_experience)
        new_experience_id = len(data['experience']) - 1

        return jsonify({
            'message': 'New experience created',
            'id': new_experience_id
        }), 201


@app.route('/resume/education', methods=['GET', 'POST'])
def education():
    '''
    Handles education requests
    '''
    if request.method == 'GET':
        return jsonify([edu.__dict__ for edu in data['education']]), 200

    if request.method == 'POST':

        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        request_body = request.get_json()

        required_fields = {
            'course': str,
            'school': str,
            'start_date': str,
            'end_date': str,
            'grade': str,
            'logo': str
        }

        missing_fields = []
        invalid_fields = []

        for field, field_type in required_fields.items():
            if field not in request_body:
                missing_fields.append(field)
            elif not isinstance(request_body[field], field_type):
                invalid_fields.append(field)

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        if invalid_fields:
            return jsonify({
                'error': 'Invalid field types',
                'invalid_fields': invalid_fields
            }), 400

        new_education = Education(
            request_body['course'],
            request_body['school'],
            request_body['start_date'],
            request_body['end_date'],
            request_body['grade'],
            request_body['logo']
        )

        data['education'].append(new_education)
        new_education_id = len(data['education']) - 1

        return jsonify({
            'message': 'New education created',
            'id': new_education_id
        }), 201


@app.route('/resume/skill', methods=['GET', 'POST'])
def skill():
    '''
    Handles skill requests
    '''
    if request.method == 'GET':
        return jsonify([skill.__dict__ for skill in data['skill']]), 200

    if request.method == 'POST':

        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        request_body = request.get_json()

        required_fields = {
            'name': str,
            'proficiency': str,
            'logo': str
        }

        missing_fields = []
        invalid_fields = []

        for field, field_type in required_fields.items():
            if field not in request_body:
                missing_fields.append(field)
            elif not isinstance(request_body[field], field_type):
                invalid_fields.append(field)

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        if invalid_fields:
            return jsonify({
                'error': 'Invalid field types',
                'invalid_fields': invalid_fields
            }), 400

        new_skill = Skill(
            request_body['name'],
            request_body['proficiency'],
            request_body['logo']
        )

        data['skill'].append(new_skill)
        new_skill_id = len(data['skill']) - 1

        return jsonify({
            'message': 'New skill created',
            'id': new_skill_id
        }), 201


@app.route('/resume/user_information', methods=['GET', 'POST', 'PUT'])
def user_information():
    '''
    Handles User Information requests
    '''
    if request.method == 'GET':
        return jsonify(data['user_information']), 200

    error = validate_fields(
        ['name', 'email_address', 'phone_number'], request.json)

    is_valid_phone_number = validate_phone_number(request.json['phone_number'])

    if not is_valid_phone_number:
        return jsonify({'error': 'Invalid phone number'}), 400
    if error:
        return jsonify({'error': ', '.join(error) + ' parameter(s) is required'}), 400

    if request.method in ('POST', 'PUT'):
        data['user_information'] = request.json
        return jsonify(data['user_information']), 201

    return jsonify({'error': 'Nothing changed'}), 400

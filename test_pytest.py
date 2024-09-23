'''
Tests in Pytest
'''
import pytest
from app import app, reset_data
from helpers import validate_fields, validate_phone_number

@pytest.fixture
def client():
    """Fixture for creating a test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def before_each_test():
    """
    Resets data before each test to ensure every test is independent of one another.
    Runs before every test.
    """
    reset_data()

def test_index(client):
    """Test the index route."""
    response = client.get('/')

    assert response.status_code == 200
    assert response.data == b"Welcome to MLH 24.FAL.A.2 Orientation API Project!!"

def test_client(client):
    """Makes a request and checks the message received is the same."""
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json['message'] == "Hello, World!"


def test_experience(client):
    """Add a new experience and check if it's returned in the list."""
    example_experience = {
        "title": "Software Developer",
        "company": "A Cooler Company",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "default.jpg"
    }
    post_response = client.post('/resume/experience', json=example_experience)
    assert post_response.status_code == 201
    item_id = post_response.json['id']
    get_response = client.get('/resume/experience')
    assert get_response.status_code == 200
    assert get_response.json[item_id]['title'] == example_experience['title']
    assert get_response.json[item_id]['company'] == example_experience['company']

def test_education(client):
    """Add a new education and check if it's returned in the list."""
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "default.jpg"
    }
    post_response = client.post('/resume/education', json=example_education)
    assert post_response.status_code == 201
    item_id = post_response.json['id']
    get_response = client.get('/resume/education')
    assert get_response.status_code == 200
    assert get_response.json[item_id]['course'] == example_education['course']
    assert get_response.json[item_id]['school'] == example_education['school']

def test_skill(client):
    """Add a new skill and check if it's returned in the list."""
    example_skill = {
        "name": "JavaScript",
        "proficiency": "2-4 years",
        "logo": "default.jpg"
    }

    post_response = client.post('/resume/skill', json=example_skill)
    assert post_response.status_code == 201
    item_id = post_response.json['id']
    get_response = client.get('/resume/skill')
    assert get_response.status_code == 200
    assert get_response.json[item_id]['name'] == example_skill['name']
    assert get_response.json[item_id]['proficiency'] == example_skill['proficiency']

def test_post_user_information(client):
    """Test the POST request for user information."""
    new_user_info = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+237680162416"
    }
    response = client.post('/resume/user_information', json=new_user_info)
    assert response.status_code == 201
    assert response.json['name'] == new_user_info['name']
    assert response.json['email_address'] == new_user_info['email_address']
    assert response.json['phone_number'] == new_user_info['phone_number']

def test_validate_fields_all_present():
    """Expect no missing fields."""
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+123456789"
    }
    result = validate_fields(
        ["name", "email_address", "phone_number"], request_data
    )

    assert result == []

def test_validate_fields_missing_field():
    """Expect 'phone_number' to be missing."""
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com"
    }

    result = validate_fields(
        ["name", "email_address", "phone_number"], request_data
    )

    assert result == ["phone_number"]

def test_valid_phone_number():
    """Test a valid properly internationalized phone number returns True."""
    valid_phone = "+14155552671"
    assert validate_phone_number(valid_phone) is True

def test_invalid_phone_number():
    """Test an invalid phone number returns False."""
    invalid_phone = "123456"
    assert validate_phone_number(invalid_phone) is False


def test_delete_skill(client):
    '''
    Test the skill deletion endpoint for skill ID bounds checking.
    '''
    # Attempt to delete a valid skill in between some invalid attempts.
    for skill_indices, expected_status_code in [
        (range(1, 5), 404), (range(0, 1), 200), (range(0, 5), 404)
    ]:
        for index in skill_indices:
            response = client.delete(f'/resume/skill/{index}')
            assert response.status_code == expected_status_code

            if expected_status_code == 200:
                assert response.json["message"] == "Skill successfully deleted"
            else:
                assert response.json["error"] == "Skill not found"


def test_upgrade_experience():
    '''
    Test the update experience endpoint for experience ID bounds checking.
    Updates the only experience and check if the update was successful.
    Check if the previous experience is not found.
    '''
    # Test some invalid experience indices (only index 0 is valid initially).
    for index in range(2, 5):
        response = app.test_client().put(f'/resume/experience/{index}')
        assert response.status_code == 400

    # Update the only experience.
    new_example_experience = {
        "title": "Software Developer",
        "company": "A Cooler Company",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "default.jpg"
    }
    response = app.test_client().put('/resume/experience/0', json=new_example_experience)
    assert response.status_code == 204

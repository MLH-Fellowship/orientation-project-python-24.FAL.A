'''
Tests in Pytest
'''
import pytest
from app import app, reset_data
from helpers import validate_fields, validate_phone_number


@pytest.fixture(autouse=True)
def before_each_test():
    """
    Resets data before each test to ensure every test is independent of one another.
    Runs before every test.
    """
    reset_data()


def test_client():
    '''
    Makes a request and checks the message received is the same
    '''
    response = app.test_client().get('/test')
    assert response.status_code == 200
    assert response.json['message'] == "Hello, World!"


def test_experience():
    '''
    Add a new experience and then get all experiences. 

    Check that it returns the new experience in that list
    '''
    example_experience = {
        "title": "Software Developer",
        "company": "A Cooler Company",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "default.jpg"
    }

    item_id = app.test_client().post('/resume/experience',
                                     json=example_experience).json['id']
    response = app.test_client().get('/resume/experience')
    assert response.json[item_id] == example_experience


def test_education():
    '''
    Add a new education and then get all educations. 

    Check that it returns the new education in that list
    '''
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "default.jpg"
    }
    item_id = app.test_client().post('/resume/education',
                                     json=example_education).json['id']

    response = app.test_client().get('/resume/education')
    assert response.json[item_id] == example_education


def test_skill():
    '''
    Add a new skill and then get all skills. 

    Check that it returns the new skill in that list
    '''
    example_skill = {
        "name": "JavaScript",
        "proficiency": "2-4 years",
        "logo": "default.jpg"
    }

    item_id = app.test_client().post('/resume/skill',
                                     json=example_skill).json['id']

    response = app.test_client().get('/resume/skill')
    assert response.json[item_id] == example_skill


def test_post_user_information():
    '''
    Test the POST request for user information.
    It should allow setting user information and return status code 201.
    '''
    new_user_info = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+237680162416"

    }
    response = app.test_client().post('/resume/user_information', json=new_user_info)
    assert response.status_code == 201
    assert response.json['name'] == new_user_info['name']
    assert response.json['email_address'] == new_user_info['email_address']
    assert response.json['phone_number'] == new_user_info['phone_number']


def test_validate_fields_all_present():
    '''
    Expect no missing fields
    '''
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+123456789"
    }

    result = validate_fields(
        ["name", "email_address", "phone_number"], request_data)

    assert result == []


def test_validate_fields_missing_field():
    '''
    Expect 'phone_number' to be missing
    '''
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com"
    }

    result = validate_fields(
        ["name", "email_address", "phone_number"], request_data)

    assert result == ["phone_number"]


def test_valid_phone_number():
    '''
    Test a valid properly internationalized phone number returns True.
    '''
    valid_phone = "+14155552671"
    assert validate_phone_number(valid_phone) is True


def test_invalid_phone_number():
    '''
    Test an invalid phone number returns False.
    '''
    invalid_phone = "123456"
    assert validate_phone_number(invalid_phone) is False


def test_delete_skill():
    '''
    Test the skill deletion endpoint for skill ID bounds checking.
    '''
    # Attempt to delete a valid skill in between some invalid attempts.
    for skill_indices, expected_status_code in [
        (range(1, 5), 404), (range(0, 1), 200), (range(0, 5), 404)
    ]:
        for index in skill_indices:
            response = app.test_client().delete(f'/resume/skill/{index}')
            assert response.status_code == expected_status_code

            if expected_status_code == 200:
                assert response.json["message"] == "Skill successfully deleted"
            else:
                assert response.json["error"] == "Skill not found"

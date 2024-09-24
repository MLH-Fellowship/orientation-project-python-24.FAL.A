"""
Tests in Pytest
"""
import json
from app import app
from helpers import validate_fields, validate_phone_number
from helpers import load_data, save_data
from models import Experience, Education, Skill, UserInformation


def test_client():
    """
    Makes a request and checks the message received is the same
    """
    response = app.test_client().get("/test")
    assert response.status_code == 200
    assert response.json["message"] == "Hello, World!"


def test_experience():
    """
    Add a new experience and then get all experiences.

    Check that it returns the new experience in that list
    """
    example_experience = {
        "title": "Software Developer",
        "company": "A Cooler Company",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "default.jpg",
    }

    item_id = (
        app.test_client().post("/resume/experience", json=example_experience).json["id"]
    )
    response = app.test_client().get("/resume/experience")
    assert any(exp["id"] == item_id for exp in response.json)



def test_education():
    """
    Add a new education and then get all educations.

    Check that it returns the new education in that list
    """
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "default.jpg",
        "id": 1
    }

    item_id = (
        app.test_client().post("/resume/education", json=example_education).json["id"]
    )

    response = app.test_client().get("/resume/education")
    assert response.json[item_id] == example_education


def test_delete_education():
    """
    Test the education deletion endpoint
    """
    # Ensure there's at least one education entry to delete
    get_response = app.test_client().get("/resume/education")
    assert get_response.status_code == 200
    initial_education_count = len(get_response.json)

    # Delete the last education entry
    last_index = initial_education_count - 1
    response = app.test_client().delete(f"/resume/education/{last_index}")
    assert response.status_code == 200
    assert response.json["message"] == "Education entry successfully deleted"

    # Verify that the education entry count has decreased by one
    get_response_after_delete = app.test_client().get("/resume/education")
    assert get_response_after_delete.status_code == 200
    assert len(get_response_after_delete.json) == initial_education_count - 1

    # Attempt to delete twice the same education entry
    response = app.test_client().delete(f"/resume/education/{last_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Education entry not found"

    # Attempt to delete an education entry with the out of range index
    invalid_index = initial_education_count + 1
    response = app.test_client().delete(f"/resume/education/{invalid_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Education entry not found"


def test_skill():
    """
    Add a new skill and then get all skills.

    Check that it returns the new skill in that list
    """

    example_skill = {
        "name": "JavaScript",
        "proficiency": "2-4 years",
        "logo": "default.jpg",
    }

    item_id = app.test_client().post("/resume/skill", json=example_skill).json["id"]

    response = app.test_client().get("/resume/skill")
    assert response.json[item_id] == example_skill


def test_post_user_information():
    """
    Test the POST request for user information.
    It should allow setting user information and return status code 201.
    """
    new_user_info = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+237680162416",
    }
    response = app.test_client().post("/resume/user_information", json=new_user_info)
    assert response.status_code == 201
    assert response.json["name"] == new_user_info["name"]
    assert response.json["email_address"] == new_user_info["email_address"]
    assert response.json["phone_number"] == new_user_info["phone_number"]


def test_validate_fields_all_present():
    """
    Expect no missing fields
    """
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+123456789",
    }

    result = validate_fields(["name", "email_address", "phone_number"], request_data)

    assert result == []


def test_validate_fields_missing_field():
    """
    Expect 'phone_number' to be missing
    """
    request_data = {"name": "John Doe", "email_address": "john@example.com"}

    result = validate_fields(["name", "email_address", "phone_number"], request_data)

    assert result == ["phone_number"]


def test_valid_phone_number():
    """
    Test a valid properly internationalized phone number returns True.
    """
    valid_phone = "+14155552671"
    assert validate_phone_number(valid_phone) is True


def test_invalid_phone_number():
    """
    Test an invalid phone number returns False.
    """
    invalid_phone = "123456"
    assert validate_phone_number(invalid_phone) is False


def test_post_skill():
    """
    Test POST
    """
    new_skill = {"name": "Python", "proficiency": "Intermediate", "logo": "default.jpg"}
    response = app.test_client().post("/resume/skill", json=new_skill)
    assert response.status_code == 201
    assert response.json["message"] == "New skill created"



def test_add_custom_section():
    """
    Test the addition of a custom section to the resume.
    """
    example_section = {
        "title": "Certifications",
        "content": "AWS Certified Solutions Architect",
    }

    response = app.test_client().post("/custom-section", json=example_section)
    assert response.status_code == 201
    assert response.json["message"] == "Custom section added"


def test_get_custom_sections():
    """
    Test retrieving all custom sections.
    """
    response = app.test_client().get("/custom-sections")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_load_data(tmpdir):
    # Create a temporary file path
    filename = tmpdir.join('data.json')

    sample_data = {
        "experience": [{"title": "Developer", "company": "Company A", "start_date": "2021", "end_date": "2022", "description": "Development", "logo": "logo.png"}],
        "education": [{"course": "CS", "school": "Tech University", "start_date": "2018", "end_date": "2022", "grade": "90", "logo": "logo.png"}],
        "skill": [{"name": "Python", "proficiency": "Expert", "logo": "logo.png"}],
        "user_information": [{"name": "John Doe", "email_address": "john@example.com", "phone_number": "+123456789"}]
    }

    with open(filename, 'w') as file:
        json.dump(sample_data, file)

    loaded_data = load_data(str(filename))

    # Assert that the data was loaded correctly
    assert len(loaded_data['experience']) == 1
    assert loaded_data['experience'][0].title == "Developer"
    assert loaded_data['user_information'][0].name == "John Doe"


def test_save_data(tmpdir):
    # Create a temporary file path
    filename = tmpdir.join('data.json')

    data = {
        "experience": [Experience("Developer", "Company A", "2021", "2022", "Development", "logo.png")],
        "education": [Education("CS", "Tech University", "2018", "2022", "90", "logo.png")],
        "skill": [Skill("Python", "Expert", "logo.png")],
        "user_information": [UserInformation("John Doe", "john@example.com", "+123456789")]
    }

    save_data(str(filename), data)

    with open(filename, 'r') as file:
        saved_data = json.load(file)

    # Assert that the file contains the correct data
    assert saved_data['experience'][0]['title'] == "Developer"
    assert saved_data['user_information'][0]['name'] == "John Doe"
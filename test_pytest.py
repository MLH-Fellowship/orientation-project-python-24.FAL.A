"""
Tests in Pytest
"""

import pytest
from app import app, data
from helpers import validate_fields, validate_phone_number
from models import Experience, Education, Skill


@pytest.fixture
def client():
    """Fixture to provide a Flask test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_data():
    """Reset the data to its initial state before each test."""
    global data
    data = {
        "experience": [
            Experience(
                "Software Developer",
                "A Cool Company",
                "October 2022",
                "Present",
                "Writing Python Code",
                "example-logo.png",
            )
        ],
        "education": [
            Education(
                "Computer Science",
                "University of Tech",
                "September 2019",
                "July 2022",
                "80%",
                "example-logo.png",
            )
        ],
        "skill": [Skill("Python", "1-2 Years", "example-logo.png")],
        "user_information": {"name": "", "email_address": "", "phone_number": ""},
    }


def test_index(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200


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
        "logo": "default.jpg",
    }
    item_id = client.post("/resume/experience", json=example_experience).json["id"]
    response = client.get("/resume/experience")
    assert response.json[item_id] == example_experience


def test_education(client):
    """Add a new education and check if it's returned in the list."""
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "default.jpg",
    }
    item_id = client.post("/resume/education", json=example_education).json["id"]
    response = client.get("/resume/education")
    assert response.json[item_id] == example_education


def test_delete_education(client):
    """Test the education deletion endpoint."""
    get_response = client.get("/resume/education")
    assert get_response.status_code == 200
    initial_education_count = len(get_response.json)

    last_index = initial_education_count - 1
    response = client.delete(f"/resume/education/{last_index}")
    assert response.status_code == 200
    assert response.json["message"] == "Education entry successfully deleted"

    get_response_after_delete = client.get("/resume/education")
    assert get_response_after_delete.status_code == 200
    assert len(get_response_after_delete.json) == initial_education_count - 1

    response = client.delete(f"/resume/education/{last_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Education entry not found"

    invalid_index = initial_education_count + 1
    response = client.delete(f"/resume/education/{invalid_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Education entry not found"


def test_skill(client):
    """Add a new skill and check if it's returned in the list."""
    example_skill = {
        "name": "JavaScript",
        "proficiency": "2-4 years",
        "logo": "default.jpg",
    }
    item_id = client.post("/resume/skill", json=example_skill).json["id"]
    response = client.get("/resume/skill")
    assert response.json[item_id] == example_skill


def test_delete_skill(client):
    """Test the skill deletion endpoint for skill ID bounds checking."""
    for index in range(2, 5):
        response = client.delete(f'/resume/skill/{index}')
        assert response.status_code == 404
        assert response.json["error"] == "Skill not found"
    
    for _ in range(2):
        response = client.delete('/resume/skill/0')
        assert response.status_code == 200
        assert response.json["message"] == "Skill successfully deleted"

    for index in range(0, 4):
        response = client.delete(f'/resume/skill/{index}')
        assert response.status_code == 404
        assert response.json["error"] == "Skill not found"


def test_post_user_information(client):
    """Test the POST request for user information."""
    new_user_info = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+237680162416",
    }
    response = client.post("/resume/user_information", json=new_user_info)
    assert response.status_code == 201
    assert response.json["name"] == new_user_info["name"]
    assert response.json["email_address"] == new_user_info["email_address"]
    assert response.json["phone_number"] == new_user_info["phone_number"]


def test_spellcheck(client):
    """Test the spell check endpoint."""
    data["experience"].append(Experience(
        "Software Develper",  # Intentional typo
        "A Cool Company",
        "October 2022",
        "Present",
        "Writting Python Code",  # Intentional typo
        "example-logo.png"
    ))

    data["education"].append(Education(
        "Comptuer Science",  
        "University of Tech",
        "September 2019",
        "July 2022",
        "80%",
        "example-logo.png"
    ))

    data["skill"].append(Skill("Pythn", "1-2 Years", "example-logo.png"))  

    request_body = {
        "experience": [
            {"title": "Software Develper", "description": "Writting Python Code"}
        ],
        "education": [
            {"course": "Comptuer Science"}
        ],
        "skill": [
            {"name": "Pythn"}
        ]
    }

    response = client.post('/resume/spellcheck', json=request_body)
    assert response.status_code == 200
    results = response.json

    assert any(r["before"] == "Software Develper" for r in results)
    assert any(r["after"] != "Software Develper" for r in results)
    assert any(r["before"] == "Writting Python Code" for r in results)
    assert any(r["after"] != "Writting Python Code" for r in results)
    assert any(r["before"] == "Comptuer Science" for r in results)
    assert any(r["after"] != "Comptuer Science" for r in results)
    assert any(r["before"] == "Pythn" for r in results)
    assert any(r["after"] != "Pythn" for r in results)


def test_validate_fields_all_present():
    """Expect no missing fields."""
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+123456789",
    }
    result = validate_fields(["name", "email_address", "phone_number"], request_data)
    assert result == []


def test_validate_fields_missing_field():
    """Expect 'phone_number' to be missing."""
    request_data = {
        "name": "John Doe",
        "email_address": "john@example.com",
    }
    result = validate_fields(["name", "email_address", "phone_number"], request_data)
    assert result == ["phone_number"]


def test_valid_phone_number():
    """Test a valid properly internationalized phone number returns True."""
    valid_phone = "+14155552671"
    assert validate_phone_number(valid_phone) is True


def test_invalid_phone_number():
    """Test an invalid phone number returns False."""
    invalid_phone = "123456"
    assert validate_phone_number(invalid_phone) is False

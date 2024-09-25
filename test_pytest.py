"""
Tests in Pytest
"""

import json, io
import pytest
from app import app, data
from helpers import validate_fields, validate_phone_number, load_data, save_data
from models import Experience, Education, Skill, UserInformation


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
    response = client.get("/")
    assert response.status_code == 200


def test_client(client):
    """Makes a request and checks the message received is the same."""
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json["message"] == "Hello, World!"


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
    item_id = client.post("/resume/experience", data=example_experience).json["id"]
    response = client.get("/resume/experience")
    assert any(exp["id"] == item_id for exp in response.json)


def test_delete_experience(client):
    """Test the experience deletion endpoint."""
    get_response = client.get("/resume/experience")
    assert get_response.status_code == 200
    initial_experience_count = len(get_response.json)

    last_index = initial_experience_count - 1
    response = client.delete(f"/resume/experience/{last_index}")
    assert response.status_code == 200
    assert response.json["message"] == "Experience entry successfully deleted"

    get_response_after_delete = client.get("/resume/experience")
    assert get_response_after_delete.status_code == 200
    assert len(get_response_after_delete.json) == initial_experience_count - 1

    response = client.delete(f"/resume/experience/{last_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Experience entry not found"

    invalid_index = initial_experience_count + 1
    response = client.delete(f"/resume/experience/{invalid_index}")
    assert response.status_code == 404
    assert response.json["error"] == "Experience entry not found"


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
    item_id = (
        app.test_client().post("/resume/education", json=example_education).json["id"]
    )

    response = app.test_client().get("/resume/education")
    # append the item_id to the example_education dictionary
    example_education["id"] = item_id + 1
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


def test_post_education_with_file_upload(client):
    """Test the POST request for education with file upload."""
    data = {
        "course": "Computer Science",
        "school": "University of Awesome",
        "start_date": "2020",
        "end_date": "2024",
        "grade": "A",
    }
    logo_data = {
        "logo": (io.BytesIO(b"fake image data"), "test-logo.jpg"),
    }

    response = client.post(
        "/resume/education",
        data={**data, **logo_data},
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert "id" in response.json


def test_put_education_with_file_upload(client):
    """Test the PUT request for updating education with file upload."""
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "default.jpg",
    }
    item_id = client.post("/resume/education", json=example_education).json["id"]

    update_data = {
        "course": "Updated Engineering",
        "school": "Updated NYU",
        "start_date": "October 2023",
        "end_date": "August 2025",
        "grade": "90%",
    }
    logo_data = {
        "logo": (io.BytesIO(b"fake image data"), "updated-logo.jpg"),
    }

    response = client.put(
        f"/resume/education/{item_id}",
        data={**update_data, **logo_data},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.json["message"] == "Education entry updated"


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
    """Test the skill deletion endpoint: remove all existing skills, add one, remove it, and attempt to remove it again."""

    initial_skills = client.get("/resume/skill").json
    for _ in range(len(initial_skills)):
        response = client.delete(f"/resume/skill/{0}")
        assert response.status_code == 200
        assert response.json["message"] == "Skill successfully deleted"

    # Add one skill
    new_skill = {"name": "Python", "proficiency": "Expert"}
    response = client.post("/resume/skill", json=new_skill)
    assert response.status_code == 201
    assert response.json["message"] == "New skill created"

    response = client.delete("/resume/skill/0")
    assert response.status_code == 200
    assert response.json["message"] == "Skill successfully deleted"

    response = client.delete("/resume/skill/0")
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
    data["experience"].append(
        Experience(
            "Software Develper",  # Intentional typo
            "A Cool Company",
            "October 2022",
            "Present",
            "Writting Python Code",  # Intentional typo
            "example-logo.png",
        )
    )

    data["education"].append(
        Education(
            "Comptuer Science",
            "University of Tech",
            "September 2019",
            "July 2022",
            "80%",
            "example-logo.png",
        )
    )

    data["skill"].append(Skill("Pythn", "1-2 Years", "example-logo.png"))

    request_body = {
        "experience": [
            {"title": "Software Develper", "description": "Writting Python Code"}
        ],
        "education": [{"course": "Comptuer Science"}],
        "skill": [{"name": "Pythn"}],
    }

    response = client.post("/resume/spellcheck", json=request_body)
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


def test_load_data(tmpdir):
    # Create a temporary file path
    filename = tmpdir.join("data.json")

    sample_data = {
        "experience": [
            {
                "title": "Developer",
                "company": "Company A",
                "start_date": "2021",
                "end_date": "2022",
                "description": "Development",
                "logo": "logo.png",
            }
        ],
        "education": [
            {
                "course": "CS",
                "school": "Tech University",
                "start_date": "2018",
                "end_date": "2022",
                "grade": "90",
                "logo": "logo.png",
            }
        ],
        "skill": [{"name": "Python", "proficiency": "Expert", "logo": "logo.png"}],
        "user_information": [
            {
                "name": "John Doe",
                "email_address": "john@example.com",
                "phone_number": "+123456789",
            }
        ],
    }

    with open(filename, "w") as file:
        json.dump(sample_data, file)

    loaded_data = load_data(str(filename))

    # Assert that the data was loaded correctly
    assert len(loaded_data["experience"]) == 1
    assert loaded_data["experience"][0].title == "Developer"
    assert loaded_data["user_information"][0].name == "John Doe"


def test_save_data(tmpdir):
    # Create a temporary file path
    filename = tmpdir.join("data.json")

    data = {
        "experience": [
            Experience(
                "Developer", "Company A", "2021", "2022", "Development", "logo.png"
            )
        ],
        "education": [
            Education("CS", "Tech University", "2018", "2022", "90", "logo.png")
        ],
        "skill": [Skill("Python", "Expert", "logo.png")],
        "user_information": [
            UserInformation("John Doe", "john@example.com", "+123456789")
        ],
    }

    save_data(str(filename), data)

    with open(filename, "r") as file:
        saved_data = json.load(file)

    # Assert that the file contains the correct data
    assert saved_data["experience"][0]["title"] == "Developer"
    assert saved_data["user_information"][0]["name"] == "John Doe"

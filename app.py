"""
Flask Application for Resume Management
"""

import os
import logging

from spellchecker import SpellChecker
from flask_cors import CORS

from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_from_directory
from models import Experience, Education, Skill, UserInformation
from helpers import (
    validate_fields,
    validate_phone_number,
    load_data,
    save_data,
    generate_id,
)


spell = SpellChecker()

# Configure logging
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads/"
DEFAULT_LOGO = "default.jpg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

data = load_data("data/data.json")


def reset_data():
    """
    Resets the values stored in data to placeholders.
    """
    data.clear()
    data["experience"] = [
        Experience(
            "Software Developer",
            "A Cool Company",
            "October 2022",
            "Present",
            "Writing Python Code",
            "example-logo.png",
        ),
    ]
    data["education"] = [
        Education(
            "Computer Science",
            "University of Tech",
            "September 2019",
            "July 2022",
            "80%",
            "example-logo.png",
        ),
    ]
    data["skill"] = [
        Skill("Python", "1-2 Years", "example-logo.png"),
    ]
    data["user_information"] = [
        UserInformation("Joe Smith", "example@gmail.com", "+11234567890"),
    ]


# reset_data()


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    :param filename: The name of the file to check
    :return: True if the file extension is allowed, False otherwise
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_missing_invalid_fields(request_body, required_fields):
    """
    Check for missing and invalid fields in the request body.

    :param request_body: The body of the request (either JSON or form data)
    :param required_fields: A dictionary of field names and their expected types
    :return: A tuple (missing_fields, invalid_fields)
    """
    missing_fields = [field for field in required_fields if field not in request_body]
    invalid_fields = [
        field
        for field, field_type in required_fields.items()
        if field in request_body and not isinstance(request_body[field], field_type)
    ]
    return missing_fields, invalid_fields


@app.route("/", strict_slashes=False)
def home():
    """
    Returns a welcome message for the app
    """
    return "Welcome to MLH 24.FAL.A.2 Orientation API Project!!"


@app.route("/test")
def hello_world():
    """
    Returns a JSON test message
    """
    return jsonify({"message": "Hello, World!"})


@app.route("/resume/experience", methods=["GET", "POST"])
def experience():
    """
    Handle experience requests for GET and POST methods
    """
    if request.method == "GET":
        return jsonify([exp.__dict__ for exp in data["experience"]]), 200

    if request.method == "POST":
        request_body = (
            request.form
            if request.content_type == "multipart/form-data"
            else request.get_json()
        )
        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {
            "title": str,
            "company": str,
            "start_date": str,
            "end_date": str,
            "description": str,
        }
        missing_fields, invalid_fields = handle_missing_invalid_fields(
            request_body, required_fields
        )

        if missing_fields or invalid_fields:
            return (
                jsonify(
                    {
                        "error": "Validation failed",
                        "missing_fields": missing_fields,
                        "invalid_fields": invalid_fields,
                    }
                ),
                400,
            )

        # Handle logo file
        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        # Create new experience
        new_id = generate_id(data, "experience")

        # Create new experience
        new_experience = Experience(
            request_body["title"],
            request_body["company"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["description"],
            logo_filename,
            new_id,
        )
        data["experience"].append(new_experience)
        save_data("data/data.json", data)
        new_experience_index = len(data["experience"]) - 1
        return (
            jsonify({"message": "New experience created", "id": new_experience_index}),
            201,
        )

    return 400


@app.route("/resume/experience/<int:index>", methods=["DELETE"])
def delete_experience(index):
    """
    Delete experience entry by index
    """
    if 0 <= index < len(data["experience"]):
        data["experience"].pop(index)
        return jsonify({"message": "Experience entry successfully deleted"}), 200
    return jsonify({"error": "Experience entry not found"}), 404


@app.route("/resume/education", methods=["GET", "POST"])
def education():
    """
    Handle education requests for GET and POST methods.
    POST: Add a new education entry with optional file upload.
    """
    if request.method == "GET":
        return jsonify([edu.__dict__ for edu in data["education"]]), 200

    if request.method == "POST":
        if request.content_type.startswith('multipart/form-data'):
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {
            "course": str,
            "school": str,
            "start_date": str,
            "end_date": str,
            "grade": str,
        }
        missing_fields, invalid_fields = handle_missing_invalid_fields(
            request_body, required_fields
        )

        if missing_fields or invalid_fields:
            return jsonify({
                "error": "Validation failed",
                "missing_fields": missing_fields,
                "invalid_fields": invalid_fields
            }), 400

        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        new_id = generate_id(data, 'education')

        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            logo_filename,
            new_id
        )
        data["education"].append(new_education)
        save_data('data/data.json', data)
        new_education_index = len(data["education"]) - 1
        return jsonify({"message": "New education created", "id": new_education_index}), 201

    return 400


@app.route("/resume/experience/<int:index>", methods=["GET"])
def experience_by_index(index):
    """
    Retrieve experience by index
    """
    if 0 <= index < len(data["experience"]):
        return jsonify(data["experience"][index].__dict__), 200
    return jsonify({"error": "Experience not found"}), 404


@app.route("/resume/education/<int:index>", methods=["GET"])
def education_by_index(index):
    """
    Retrieve education by index
    """
    if 0 <= index < len(data["education"]):
        return jsonify(data["education"][index].__dict__), 200
    return jsonify({"error": "Education not found"}), 404


@app.route("/resume/education/<int:index>", methods=["DELETE"])
def delete_education(index):
    """
    Delete education entry by index
    """
    if 0 <= index < len(data["education"]):
        data["education"].pop(index)
        return jsonify({"message": "Education entry successfully deleted"}), 200
    return jsonify({"error": "Education entry not found"}), 404


@app.route("/resume/education/<int:index>", methods=["PUT"])
def update_education(index):
    """
    Update education entry by index.
    Supports updating both text fields and file upload for logo.
    """
    if 0 <= index < len(data["education"]):
        if request.content_type.startswith('multipart/form-data'):
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        edu = data["education"][index]

        edu.course = request_body.get("course", edu.course)
        edu.school = request_body.get("school", edu.school)
        edu.start_date = request_body.get("start_date", edu.start_date)
        edu.end_date = request_body.get("end_date", edu.end_date)
        edu.grade = request_body.get("grade", edu.grade)

        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                edu.logo = filename

        save_data('data/data.json', data)
        return jsonify({"message": "Education entry updated", "id": index}), 200

    return jsonify({"error": "Education entry not found"}), 404


@app.route("/resume/skill", methods=["GET", "POST"])
def skill():
    """
    Handle skill requests
    """
    if request.method == "GET":
        return jsonify([sk.__dict__ for sk in data["skill"]]), 200

    if request.method == "POST":
        request_body = (
            request.form
            if request.content_type == "multipart/form-data"
            else request.get_json()
        )
        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {"name": str, "proficiency": str}
        missing_fields, invalid_fields = handle_missing_invalid_fields(
            request_body, required_fields
        )

        if missing_fields or invalid_fields:
            return (
                jsonify(
                    {
                        "error": "Validation failed",
                        "missing_fields": missing_fields,
                        "invalid_fields": invalid_fields,
                    }
                ),
                400,
            )

        # Handle logo file
        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        # Create new skill
        new_skill = Skill(
            request_body["name"], request_body["proficiency"], logo_filename
        )
        data["skill"].append(new_skill)

        save_data("data/data.json", data)
        return (
            jsonify({"message": "New skill created", "id": len(data["skill"]) - 1}),
            201,
        )

    return 400


@app.route("/resume/user_information", methods=["GET", "POST", "PUT"])
def user_information():
    """
    Handle user information requests
    """
    if request.method == "GET":
        return jsonify(data["user_information"]), 200

    error = validate_fields(["name", "email_address", "phone_number"], request.json)

    is_valid_phone_number = validate_phone_number(request.json["phone_number"])
    if not is_valid_phone_number:
        return jsonify({"error": "Invalid phone number"}), 400
    if error:
        return jsonify({"error": f"{', '.join(error)} parameter(s) is required"}), 400

    if request.method in ("POST", "PUT"):
        data["user_information"] = request.json
        return jsonify(data["user_information"]), 201

    return 400


@app.route("/resume/skill/<int:index>", methods=["DELETE"])
def delete_skill(index):
    """
    Delete skill by index
    """
    if 0 <= index < len(data["skill"]):
        removed_skill = data["skill"].pop(index)
        logging.info("Skill deleted: %s", removed_skill.name)
        save_data("data/data.json", data)
        return jsonify({"message": "Skill successfully deleted"}), 200
    return jsonify({"error": "Skill not found"}), 404


@app.route("/resume/spellcheck", methods=["POST"])
def spellcheck():
    """
    Spellcheck the resume.
    (TODO add more detailed info here)
    """
    request_body = request.get_json()
    if not request_body:
        return jsonify({"error": "Request must be JSON"}), 400

    results = []

    for exp in request_body.get("experience", []):
        title = exp.get("title", "")
        description = exp.get("description", "")
        if title:
            results.append(
                {
                    "before": title,
                    "after": (
                        list(spell.candidates(title)) if spell.candidates(title) else []
                    ),
                }
            )
        if description:
            results.append(
                {
                    "before": description,
                    "after": (
                        list(spell.candidates(description))
                        if spell.candidates(description)
                        else []
                    ),
                }
            )

    for edu in request_body.get("education", []):
        course = edu.get("course", "")
        if course:
            results.append(
                {
                    "before": course,
                    "after": (
                        list(spell.candidates(course))
                        if spell.candidates(course)
                        else []
                    ),
                }
            )

    for sk in request_body.get("skill", []):
        name = sk.get("name", "")
        if name:
            results.append(
                {
                    "before": name,
                    "after": (
                        list(spell.candidates(name)) if spell.candidates(name) else []
                    ),
                }
            )

    return jsonify(results), 200


@app.route("/custom-section", methods=["POST"])
def add_custom_section():
    """
    Add a new custom section to the resume.
    Requires a title and content in the request body.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"error": "Request must be JSON"}), 400

    title = request_data.get("title")
    content = request_data.get("content")

    if not title or not content:
        return jsonify({"error": "Both 'title' and 'content' are required"}), 400

    new_section = {"title": title, "content": content}
    data["custom_sections"].append(new_section)

    section_id = len(data["custom_sections"]) - 1
    logging.info("New custom section added: %s", title)
    return jsonify({"message": "Custom section added", "id": section_id}), 201


@app.route("/custom-sections", methods=["GET"])
def get_custom_sections():
    """
    Retrieve all custom sections added by the user.
    """
    return jsonify(data["custom_sections"]), 200


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """
    Function for serving uploaded files from /uploads.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

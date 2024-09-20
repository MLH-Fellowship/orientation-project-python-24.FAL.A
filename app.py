"""
Flask Application for Resume Management
"""

import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from models import Experience, Education, Skill
from helpers import validate_fields, validate_phone_number

UPLOAD_FOLDER = "uploads/"
DEFAULT_LOGO = "default.jpg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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


@app.route("/", strict_slashes=False)
def index():
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
            request.form if request.content_type == "multipart/form-data"
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
        missing_fields, invalid_fields = handle_missing_invalid_fields(request_body, required_fields)

        if missing_fields or invalid_fields:
            return jsonify(
                {
                    "error": "Validation failed",
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields,
                }
            ), 400

        # Handle logo file
        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        # Create new experience
        new_experience = Experience(
            request_body["title"],
            request_body["company"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["description"],
            logo_filename,
        )
        data["experience"].append(new_experience)
        return jsonify({"message": "New experience created", "id": len(data["experience"]) - 1}), 201


@app.route("/resume/education", methods=["GET", "POST"])
def education():
    """
    Handle education requests for GET and POST methods
    """
    if request.method == "GET":
        return jsonify([edu.__dict__ for edu in data["education"]]), 200

    if request.method == "POST":
        request_body = request.get_json()
        if not request_body:
            return jsonify({"error": "Request must be JSON"}), 400

        required_fields = {"course": str, "school": str, "start_date": str, "end_date": str, "grade": str}
        missing_fields, invalid_fields = handle_missing_invalid_fields(request_body, required_fields)

        if missing_fields or invalid_fields:
            return jsonify({
                "error": "Validation failed",
                "missing_fields": missing_fields,
                "invalid_fields": invalid_fields
            }), 400

        # Create new education entry
        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            DEFAULT_LOGO,
        )
        data["education"].append(new_education)
        return jsonify({"message": "New education created", "id": len(data["education"]) - 1}), 201


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


@app.route("/resume/skill", methods=["GET", "POST"])
def skill():
    """
    Handle skill requests
    """
    if request.method == "GET":
        return jsonify([sk.__dict__ for sk in data["skill"]]), 200

    if request.method == "POST":
        request_body = request.form if request.content_type == "multipart/form-data" else request.get_json()
        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {"name": str, "proficiency": str}
        missing_fields, invalid_fields = handle_missing_invalid_fields(request_body, required_fields)

        if missing_fields or invalid_fields:
            return jsonify({
                "error": "Validation failed",
                "missing_fields": missing_fields,
                "invalid_fields": invalid_fields
            }), 400

        # Handle logo file
        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        # Create new skill
        new_skill = Skill(request_body["name"], request_body["proficiency"], logo_filename)
        data["skill"].append(new_skill)
        return jsonify({"message": "New skill created", "id": len(data["skill"]) - 1}), 201


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


@app.route("/resume/skill/<int:index>", methods=["DELETE"])
def delete_skill(index):
    """
    Delete skill by index
    """
    if 0 <= index < len(data["skill"]):
        data["skill"].pop(index)
        return jsonify({"message": "Skill successfully deleted"}), 200
    return jsonify({"error": "Skill not found"}), 404

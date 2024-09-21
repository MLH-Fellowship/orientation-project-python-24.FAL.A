"""
Flask Application
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


@app.route("/test")
def hello_world():
    """
    Returns a JSON test message
    """
    return jsonify({"message": "Hello, World!"})


@app.route("/resume/experience", methods=["GET", "POST"])
def experience():
    """
    Handle experience requests
    """
    if request.method == "GET":
        return jsonify([exp.__dict__ for exp in data["experience"]])

    if request.method == "POST":

        if request.content_type == "multipart/form-data":
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {
            "title": str,
            "company": str,
            "start_date": str,
            "end_date": str,
            "description": str,
        }

        missing_fields = []
        invalid_fields = []

        for field, field_type in required_fields.items():
            if field not in request_body:
                missing_fields.append(field)
            elif not isinstance(request_body[field], field_type):
                invalid_fields.append(field)

        if missing_fields:
            return (
                jsonify(
                    {
                        "error": "Missing required fields",
                        "missing_fields": missing_fields,
                    }
                ),
                400,
            )

        if invalid_fields:
            return (
                jsonify(
                    {"error": "Invalid field types", "invalid_fields": invalid_fields}
                ),
                400,
            )

        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        new_experience = Experience(
            request_body["title"],
            request_body["company"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["description"],
            logo_filename,
        )

        data["experience"].append(new_experience)

        new_experience_id = len(data["experience"]) - 1

        return (
            jsonify({"message": "New experience created", "id": new_experience_id}),
            201,
        )

    return jsonify({})


@app.route("/resume/experience/<int:index>", methods=["GET"])
def experience_by_index(index):
    """
    Handle experience requests by index.
    
    Retrieves a specific experience entry from the `data["experience"]` list based on the index.
    
    If the index is valid (within the range of the experience list), it returns the corresponding
    experience entry.
    Otherwise, it returns a 404 error with a message indicating that the experience was not found.
    
    :param index: (int) The index of the experience entry to retrieve.
    
    :returns: 
        - JSON response containing the experience entry if the index is valid.
        - JSON response containing an error message if the index is out of range.
        - HTTP status code 200 if successful, 404 if the experience is not found.
    :rtype: tuple
    """
    if 0 <= len(data["experience"]) and index < len(data["experience"]):
        return jsonify(data["experience"][index])
    return jsonify({"error": "Experience not found"}), 404


@app.route("/resume/education", methods=["GET", "POST"])
def education():
    '''
    Handles education requests
    '''
    if request.method == 'GET':
        return jsonify(data['education']), 200

    if request.method == 'POST':
        return jsonify({})

    return jsonify({})

@app.route("/resume/education/<int:index>", methods=["GET"])
def education_by_index(index=None):
    """
    Handles education requests. Supports both GET and POST methods:
    
    - GET:
        - Returns the full list of education records if no `index` is provided.
        - Returns a specific education record if a valid `index` is provided.
        - If the `index` is invalid, returns a 404 error.
    
    - POST:
        - Adds a new education record to the database.
        - Validates the required fields (`course`, `school`, `start_date`, `end_date`, `grade`)
          and ensures they are present and of the correct type.
        - If any fields are missing or invalid, returns a 400 error.
        - Optionally accepts a `logo` file, which will be saved if it is a valid file.
        - Returns a success message and the ID of the newly created record.

    :param index: (int, optional) The index of the education record to retrieve. If not provided,
    all records are returned. Defaults to None.
    
    :returns: JSON response containing the education data or error message, along with the HTTP
    status code.

    :rtype: tuple
    """
    response = {}
    status_code = 200

    if request.method == "GET":
        if index is not None:
            if index < 0 or index >= len(data["education"]):
                response = {"error": "Education not found"}
                status_code = 404
            else:
                response = data["education"][index]
        else:
            response = [edu.__dict__ for edu in data["education"]]
        return jsonify(response), status_code

    if request.method == "POST":
        request_body = (
            request.form
            if request.content_type == "multipart/form-data"
            else request.get_json()
        )

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {
            "course": str,
            "school": str,
            "start_date": str,
            "end_date": str,
            "grade": str,
        }

        missing_fields = [
            field for field in required_fields if field not in request_body
        ]
        invalid_fields = [
            field
            for field, field_type in required_fields.items()
            if field in request_body and not isinstance(request_body[field], field_type)
        ]

        if missing_fields or invalid_fields:
            response = {"error": ""}
            if missing_fields:
                response[
                    "error"
                ] += f"Missing required fields: {', '.join(missing_fields)}. "
            if invalid_fields:
                response[
                    "error"
                ] += f"Invalid field types: {', '.join(invalid_fields)}."
            return jsonify(response), 400

        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            logo_filename,
        )

        data["education"].append(new_education)

        response = {
            "message": "New education created",
            "id": len(data["education"]) - 1,
        }
        status_code = 201

    return jsonify(response), status_code


@app.route("/resume/skill", methods=["GET", "POST"])
def skill():
    """
    Handles Skill requests
    """
    if request.method == "GET":
        return jsonify([sk.__dict__ for sk in data["skill"]])

    if request.method == "POST":

        if request.content_type == "multipart/form-data":
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        required_fields = {"name": str, "proficiency": str}

        missing_fields = []
        invalid_fields = []

        for field, field_type in required_fields.items():
            if field not in request_body:
                missing_fields.append(field)
            elif not isinstance(request_body[field], field_type):
                invalid_fields.append(field)

        if missing_fields:
            return (
                jsonify(
                    {
                        "error": "Missing required fields",
                        "missing_fields": missing_fields,
                    }
                ),
                400,
            )

        if invalid_fields:
            return (
                jsonify(
                    {"error": "Invalid field types", "invalid_fields": invalid_fields}
                ),
                400,
            )

        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        new_skill = Skill(
            request_body["name"], request_body["proficiency"], logo_filename
        )

        data["skill"].append(new_skill)

        return (
            jsonify({"message": "New skill created", "id": len(data["skill"]) - 1}),
            201,
        )

    return jsonify({})


@app.route("/resume/user_information", methods=["GET", "POST", "PUT"])
def user_information():
    """
    Handles User Information requests
    """
    if request.method == "GET":
        return jsonify(data["user_information"]), 200

    error = validate_fields(["name", "email_address", "phone_number"], request.json)

    is_valid_phone_number = validate_phone_number(request.json["phone_number"])

    if not is_valid_phone_number:
        return jsonify({"error": "Invalid phone number"}), 400
    if error:
        return jsonify({"error": ", ".join(error) + " parameter(s) is required"}), 400

    if request.method in ("POST", "PUT"):
        data["user_information"] = request.json
        return jsonify(data["user_information"]), 201

    return jsonify({"error": "Nothing changed"}), 400


@app.route('/resume/skill/<int:index>', methods=['DELETE'])
def delete_skill(index):
    '''
    Handles Skill deletion requests
    '''
    if not 0 <= index < len(data["skill"]):
        return jsonify({"error": "Skill not found"}), 404

    data["skill"].pop(index)

    return jsonify({"message": "Skill successfully deleted"}), 200

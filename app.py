"""
Flask Application for Resume Management
"""

import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from models import Experience, Education, Skill
from helpers import validate_fields, validate_phone_number

# Configure logging
logging.basicConfig(level=logging.INFO)

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
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def handle_missing_invalid_fields(request_body, required_fields):
    """
    Check for missing and invalid fields in the request body.

    :param request_body: The body of the request (either JSON or form data)
    :param required_fields: A dictionary of field names and their expected types
    :return: A tuple (missing_fields, invalid_fields)
    """
    missing_fields = [
        field for field in required_fields if field not in request_body
    ]
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
    Returns a list of experiences or creates a new experience.
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
            logging.warning("Validation failed: Missing %s, Invalid %s", missing_fields, invalid_fields)
            return jsonify({"error": "Validation failed", "missing_fields": missing_fields, "invalid_fields": invalid_fields}), 400

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

        new_experience_id = len(data["experience"]) - 1
  
        logging.info("New experience added: %s", new_experience.title)
        return jsonify({"message": "New experience created", "id": new_experience_id}), 201

    return jsonify({})


@app.route("/resume/experience/<int:index>", methods=["GET", "PUT"])
def experience_by_index(index):
    """
    - GET:
        - Returns a specific experience entry if a valid `index` is provided.
        - If the `index` is invalid, returns a 404 error.
    
    - PUT:
        - Updates an existing experience entry.
        - Validates the required fields 
          (`title`, `company`, `start_date`, `end_date`, `description`)
          and ensures they are present and of the correct type.
        - If any fields are missing or invalid, returns a 400 error.
        - Optionally accepts a `logo` file, which will be saved if it is a valid file.
        - Returns a success message and the ID of the updated record.

    :param index: (int) The index of the experience record to retrieve.

    :returns: JSON response containing the experience data or error message, along with the HTTP
    status code.

    :rtype: tuple
    """
    if request.method == "GET":
        if 0 <= len(data["experience"]) and index < len(data["experience"]):
            return jsonify(data["experience"][index])
        return jsonify({"error": "Experience not found"}), 404
    if request.method == "PUT":
        if request.content_type == "multipart/form-data":
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        error = validate_fields(["title", "company", "start_date", "end_date", "description"],
                                 request_body)

        if error:
            return jsonify({"error": ", ".join(error) + " parameter(s) is required"}), 400

        logo_filename = DEFAULT_LOGO
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        data["experience"][index] = Experience(
            request_body["title"],
            request_body["company"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["description"],
            logo_filename,
        )

        return jsonify({"message": "Experience updated", "id": index}), 204
    return jsonify({}), 400


@app.route("/resume/education", methods=["GET", "POST"])
def education():
    """
    Handles education requests for GET and POST methods
    """
    if request.method == 'GET':
        return jsonify([edu.__dict__ for edu in data['education']]), 200

    if request.method == 'POST':
        request_body = request.get_json()
        if not request_body:
            return jsonify({"error": "Request must be JSON"}), 400

        required_fields = {
            "course": str,
            "school": str,
            "start_date": str,
            "end_date": str,
            "grade": str
        }
        missing_fields, invalid_fields = handle_missing_invalid_fields(
            request_body, required_fields
        )

        if missing_fields or invalid_fields:
            return (
                jsonify({
                    "error": "Validation failed",
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields
                }),
                400,
            )

        # Create new education entry
        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            DEFAULT_LOGO,
        )
        data['education'].append(new_education)
        logging.info("New education added: %s", new_education.course)
        return jsonify({"message": "New education created", "id": len(data['education']) - 1}), 201

@app.route("/resume/education/<int:edu_index>", methods=["GET"])
def education_by_index(edu_index):
    if 0 <= edu_index < len(data["education"]):
        return jsonify(data["education"][edu_index].__dict__), 200
    return jsonify({"error": "Education not found"}), 404

@app.route("/resume/skill", methods=["GET", "POST"])
def skill():
    """
    Handle skill requests
    """
    if request.method == 'GET':
        skill_id = request.args.get('id')
        if skill_id is None:
            return jsonify(data['skill']), 200
        try:
            skill_id = int(skill_id)
        except ValueError:
            return jsonify({'error': 'Invalid request'}), 400
        if 0 <= skill_id < len(data['skill']):
            return jsonify(data['skill'][skill_id]), 200

    if request.method == "POST":
        request_body = (
            request.form if request.content_type == "multipart/form-data"
            else request.get_json()
        )
        if not request_body:
            return (
                jsonify({"error": "Request must be JSON or include form data"}),
                400,
            )

        required_fields = {"name": str, "proficiency": str}
        missing_fields, invalid_fields = handle_missing_invalid_fields(
            request_body, required_fields
        )

        if missing_fields or invalid_fields:
            return (
                jsonify({
                    "error": "Validation failed",
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields
                }),
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
            request_body["name"],
            request_body["proficiency"],
            logo_filename
        )
        data["skill"].append(new_skill)
        logging.info("New skill added: %s", new_skill.name)

        return (
            jsonify({
                "message": "New skill created",
                "id": len(data["skill"]) - 1
            }),
            201,
        )


@app.route("/resume/user_information", methods=["GET", "POST", "PUT"])
def user_information():
    """
    Handle user information requests
    """
    if request.method == "GET":
        return jsonify(data["user_information"]), 200

    if request.method in ("POST", "PUT"):
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Request must be JSON"}), 400

        error = validate_fields(
            ["name", "email_address", "phone_number"], request_data
        )
        if error:
            return (
                jsonify({"error": f"{', '.join(error)} parameter(s) is required"}),
                400,
            )

        is_valid_phone_number = validate_phone_number(
            request_data["phone_number"]
        )
        if not is_valid_phone_number:
            return jsonify({"error": "Invalid phone number"}), 400

        data["user_information"] = request_data
        logging.info("User information updated for: %s", request_data['name'])
        return jsonify(data["user_information"]), 201

@app.route("/resume/skill/<int:skill_index>", methods=["DELETE"])
def delete_skill(skill_index):
    """
    Delete a skill by its index.
    
    :param skill_index: The index of the skill to delete.
    """
    if 0 <= skill_index < len(data["skill"]):
        removed_skill = data["skill"].pop(skill_index)
        logging.info("Skill deleted: %s", removed_skill.name)
        return jsonify({"message": "Skill successfully deleted"}), 200
    return jsonify({"error": "Skill not found"}), 404






if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

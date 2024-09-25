"""
Flask Application for Resume Management
"""

import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_from_directory
from models import Experience, Education, Skill, UserInformation
from helpers import validate_fields, validate_phone_number
from spellchecker import SpellChecker
from flask_cors import CORS

spell = SpellChecker()

# Configure logging
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads/"
DEFAULT_LOGO = "default.jpg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

data = {"experience": [], "education": [], "skill": [], "user_information": []}


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


reset_data()


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
        return (
            jsonify(
                {"message": "New experience created", "id": len(data["experience"]) - 1}
            ),
            201,
        )

    return jsonify({}), 200



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

        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            DEFAULT_LOGO,
        )
        data["education"].append(new_education)
        return (
            jsonify(
                {"message": "New education created", "id": len(data["education"]) - 1}
            ),
            201,
        )

    return jsonify({}), 200



@app.route("/resume/experience/<int:index>", methods=["GET"])
def experience_by_index(index):
    """
    Retrieve experience by index
    """
    if 0 <= index < len(data["experience"]):
        return jsonify(data["experience"][index].__dict__), 200
    return jsonify({"error": "Experience not found"}), 404


@app.route("/resume/education/<int:index>", methods=["GET", "PUT"])
def education_by_index(index=None):
    """
    Retrieve education by index
    """
    if request.method == "GET":
        if 0 <= index < len(data["education"]):
            return jsonify(data["education"][index].__dict__), 200
        return jsonify({"error": "Education entry not found"}), 404

    if request.method == "PUT":
        if request.content_type == "multipart/form-data":
            request_body = request.form
        else:
            request_body = request.get_json()

        if not request_body:
            return jsonify({"error": "Request must be JSON or include form data"}), 400

        error = validate_fields(
            ["course", "school", "start_date", "end_date", "grade"], request_body
        )

        if error:
            return (
                jsonify({"error": ", ".join(error) + " parameter(s) is required"}),
                400,
            )

        logo_filename = data["education"][index].logo
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        data["education"][index] = Education(
            course=request_body["course"],
            school=request_body["school"],
            start_date=request_body["start_date"],
            end_date=request_body["end_date"],
            grade=request_body["grade"],
            logo=logo_filename,
        )

        logging.info("Education updated: %s", request_body["course"])
        return jsonify({"message": "Education updated", "id": index}), 200

    return jsonify({}), 400


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
    Update an existing education entry by index.
    Accepts JSON data and optionally a logo file.
    """
    if index < 0 or index >= len(data["education"]):
        return jsonify({"error": "Education entry not found"}), 404

    if request.content_type == "multipart/form-data":
        request_body = request.form
    else:
        request_body = request.get_json()

    if not request_body:
        return jsonify({"error": "Request must be JSON or include form data"}), 400

    required_fields = ["course", "school", "start_date", "end_date", "grade"]
    missing_fields = validate_fields(required_fields, request_body)
    if missing_fields:
        return (
            jsonify({"error": f'Missing required fields: {", ".join(missing_fields)}'}),
            400,
        )

    logo_filename = data["education"][index].logo
    if "logo" in request.files:
        logo_file = request.files["logo"]
        if logo_file and allowed_file(logo_file.filename):
            filename = secure_filename(logo_file.filename)
            logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            logo_filename = filename

    data["education"][index] = Education(
        course=request_body["course"],
        school=request_body["school"],
        start_date=request_body["start_date"],
        end_date=request_body["end_date"],
        grade=request_body["grade"],
        logo=logo_filename,
    )

    logging.info("Education updated: %s", request_body["course"])
    return jsonify({"message": "Education updated", "id": index}), 200


# pylint: disable=inconsistent-return-statements
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
        return (
            jsonify({"message": "New skill created", "id": len(data["skill"]) - 1}),
            201,
        )


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


@app.route("/resume/spellcheck", methods=["POST"])
def spellcheck():
    """
    Spelling check
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

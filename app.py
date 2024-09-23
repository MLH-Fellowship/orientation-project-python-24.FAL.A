"""
Flask Application for Resume Management
"""

import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_from_directory
from models import Experience, Education, Skill, UserInformation
from helpers import validate_fields, validate_phone_number

# Configure logging
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads/"
DEFAULT_LOGO = "default.jpg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

data = {}


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
custom_sections = []


@app.route("/custom-section", methods=["POST"])
def add_custom_section():
    """
    Add a new custom section to the resume.

    The request should contain a JSON object with 'title' and 'content'.
    """
    request_data = request.get_json()

    if not request_data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "title" not in request_data or "content" not in request_data:
        return jsonify({"error": "Both 'title' and 'content' are required"}), 400

    new_section = {"title": request_data["title"], "content": request_data["content"]}

    custom_sections.append(new_section)

    return (
        jsonify(
            {"message": "Custom section added successfully", "section": new_section}
        ),
        201,
    )


@app.route("/custom-sections", methods=["GET"])
def get_custom_sections():
    """
    Retrieve all custom sections.
    """
    return jsonify(custom_sections), 200


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
    Returns a list of experiences or creates a new experience.
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
            logging.warning(
                "Validation failed: Missing %s, Invalid %s",
                missing_fields,
                invalid_fields,
            )
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
        return (
            jsonify({"message": "New experience created", "id": new_experience_id}),
            201,
        )

    return jsonify({})


@app.route("/resume/experience/<int:index>", methods=["GET", "PUT"])
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
@app.route("/resume/education/<int:index>", methods=["GET"])
def education():
    """
    Handles education requests. Supports both GET and POST methods:

    - GET:
        - Returns a list of all education records.
        - If no index is provided, returns all records.

    - POST:
        - Adds a new education record to the database.
        - Validates the required fields (`course`, `school`, `start_date`, `end_date`, `grade`)
          and ensures they are present and of the correct type.
        - If any fields are missing or invalid, returns a 400 error.
        - Optionally accepts a `logo` file, which will be saved if it is a valid file.
        - Returns a success message and the ID of the created record.
    """
    if request.method == "GET":
        return jsonify([edu.__dict__ for edu in data["education"]]), 200

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

        new_education = Education(
            request_body["course"],
            request_body["school"],
            request_body["start_date"],
            request_body["end_date"],
            request_body["grade"],
            logo_filename,
        )

        data["education"].append(new_education)
        new_education_id = len(data["education"]) - 1

        return (
            jsonify({"message": "New education created", "id": new_education_id}),
            201,
        )

    return jsonify({}), 400


@app.route("/resume/education/<int:index>", methods=["GET", "PUT"])
def education_by_index(index):
    """
    Handles education requests by index.

    - GET:
        - Returns a specific education entry if a valid `index` is provided.
        - If the `index` is invalid, returns a 404 error.

    - PUT:
        - Updates an existing education entry by index.
        - Validates the required fields (`course`, `school`, `start_date`, `end_date`, `grade`)
          and ensures they are present and of the correct type.
        - If any fields are missing or invalid, returns a 400 error.
        - Optionally accepts a `logo` file, which will be saved if it is a valid file.
        - Returns a success message and the ID of the updated record.

    :param index: (int) The index of the education record to retrieve or update.

    :returns: JSON response containing the education data or error message, along with the HTTP
    status code.
    """
    if request.method == "GET":
        if 0 <= index < len(data["education"]):
            return jsonify(data["education"][index].__dict__), 200
        return jsonify({"error": "Education entry not found"}), 404

    if request.method == "PUT":
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

        logo_filename = data["education"][index].logo
        if "logo" in request.files:
            logo_file = request.files["logo"]
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                logo_filename = filename

        data["education"][index].course = request_body["course"]
        data["education"][index].school = request_body["school"]
        data["education"][index].start_date = request_body["start_date"]
        data["education"][index].end_date = request_body["end_date"]
        data["education"][index].grade = request_body["grade"]
        data["education"][index].logo = logo_filename

        return jsonify({"message": "Education updated", "id": index}), 200

    return jsonify({}), 400


@app.route("/resume/education/<int:index>", methods=["DELETE"])
def delete_education(index):
    """
    Delete an education entry by its index

    :param index: The index of the education to delete
    """
    if 0 <= index < len(data["education"]):
        removed_education = data["education"].pop(index)
        logging.info(
            "Education deleted: %s at index %d", removed_education.course, index
        )
        return jsonify({"message": "Education entry successfully deleted"}), 200
    return jsonify({"error": "Education entry not found"}), 404


@app.route("/resume/skill", methods=["GET", "POST", "PUT"])
def skill():
    """
    Handle skill requests for GET, POST, and PUT methods.
    """
    if request.method == "GET":
        return handle_get_skill()

    if request.method == "POST":
        return handle_post_skill()

    if request.method == "PUT":
        return handle_put_skill()

    return jsonify({}), 400


def handle_get_skill():
    """
    Handle GET requests for skills.
    """
    skill_id = request.args.get("id")
    if skill_id is None:
        return jsonify([skill.__dict__ for skill in data["skill"]]), 200

    try:
        skill_id = int(skill_id)
        if 0 <= skill_id < len(data["skill"]):
            return jsonify(data["skill"][skill_id].__dict__), 200
        return jsonify({"error": "Skill not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid request"}), 400


def handle_post_skill():
    """
    Handle POST requests for creating a new skill.
    """
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

    logo_filename = save_logo_file(request.files.get("logo"))

    new_skill = Skill(request_body["name"], request_body["proficiency"], logo_filename)
    data["skill"].append(new_skill)
    return jsonify({"message": "New skill created", "id": len(data["skill"]) - 1}), 201


def handle_put_skill():
    """
    Handle PUT requests for updating an existing skill.
    """
    request_body = request.get_json()
    skill_id = request.args.get("id")

    if not skill_id or not skill_id.isdigit():
        return jsonify({"error": "Invalid skill ID"}), 400

    skill_id = int(skill_id)
    if 0 <= skill_id < len(data["skill"]):
        if not request_body:
            return jsonify({"error": "Request must be JSON"}), 400

        existing_skill = data["skill"][skill_id]
        existing_skill.name = request_body.get("name", existing_skill.name)
        existing_skill.proficiency = request_body.get(
            "proficiency", existing_skill.proficiency
        )
        existing_skill.logo = request_body.get("logo", existing_skill.logo)

        return jsonify(existing_skill.__dict__), 200

    return jsonify({"error": "Skill not found"}), 404


def save_logo_file(logo_file):
    """
    Save the logo file if provided and return the filename.
    """
    if logo_file and allowed_file(logo_file.filename):
        filename = secure_filename(logo_file.filename)
        logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return filename

    return DEFAULT_LOGO


# pylint: disable=inconsistent-return-statements
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

        error = validate_fields(["name", "email_address", "phone_number"], request_data)
        if error:
            return (
                jsonify({"error": f"{', '.join(error)} parameter(s) is required"}),
                400,
            )

        is_valid_phone_number = validate_phone_number(request_data["phone_number"])
        if not is_valid_phone_number:
            return jsonify({"error": "Invalid phone number"}), 400

        data["user_information"] = request_data
        logging.info("User information updated for: %s", request_data["name"])
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


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """
    Function for serving uploaded files from /uploads.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

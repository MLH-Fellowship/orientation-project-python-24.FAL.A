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
    Handle experience requests by index
    """
    if 0 <= len(data["experience"]) and index < len(data["experience"]):
        return jsonify(data["experience"][index])
    return jsonify({"error": "Experience not found"}), 404


@app.route("/resume/education", methods=["GET", "POST"])
@app.route("/resume/education/<int:index>", methods=["GET"])
def education(index=None):
    """
    Handles education requests
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

@app.route("/resume/education/<int:index>", methods=["DELETE"])
def delete_education(index):
    """
    Delete an education entry by its index
    
    :param index: The index of the education to delete
    """
    if 0 <= index < len(data["education"]):
        removed_education = data["education"].pop(index)
        logging.info("Education deleted: %s at index %d", removed_education.course, index)
        return jsonify({"message": "Education entry successfully deleted"}), 200
    return jsonify({"error": "Education entry not found"}), 404

@app.route("/resume/skill", methods=["GET", "POST", "PUT"])
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

    if request.method == "PUT":
        try:
            skill_id = request.args.get('id')
            if skill_id is None:
                return jsonify({'error': 'Skill not found'}), 400   
            skill_id = int(skill_id)
            if skill_id < 0 or skill_id >= len(data['skill']):
                raise IndexError
            error = validate_fields(['name', 'proficiency', 'logo'], request.json)
            if error:
                return jsonify({"error": ", ".join(error) + " parameter(s) is required"}), 400
            data['skill'][skill_id] = request.json
            return jsonify(data['skill'][skill_id]), 200
        except ValueError:
            return jsonify({'error': 'Skill not found'}), 400    
        except:
            return jsonify({'error': 'Invalid request'}), 400
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

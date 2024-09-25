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

spell = SpellChecker()

# Configure logging
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads/"
DEFAULT_LOGO = "default.jpg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

data = {
    "experience": [],
    "education": [],
    "skill": [],
    "user_information": []
}

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

# Remaining routes including '/resume/experience', '/resume/education', '/resume/skill', etc.

@app.route("/resume/spellcheck", methods=["POST"])
def spellcheck():
    request_body = request.get_json()
    if not request_body:
        return jsonify({"error": "Request must be JSON"}), 400

    results = []

    for exp in request_body.get("experience", []):
        title = exp.get("title", "")
        description = exp.get("description", "")
        if title:
            results.append({
                "before": title,
                "after": list(spell.candidates(title)) if spell.candidates(title) else []
            })
        if description:
            results.append({
                "before": description,
                "after": list(spell.candidates(description)) if spell.candidates(description) else []
            })

    for edu in request_body.get("education", []):
        course = edu.get("course", "")
        if course:
            results.append({
                "before": course,
                "after": list(spell.candidates(course)) if spell.candidates(course) else []
            })

    for sk in request_body.get("skill", []):
        name = sk.get("name", "")
        if name:
            results.append({
                "before": name,
                "after": list(spell.candidates(name)) if spell.candidates(name) else []
            })

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

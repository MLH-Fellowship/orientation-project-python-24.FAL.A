'''
Flask Application
'''
from flask import Flask, jsonify, request
from models import Experience, Education, Skill

app = Flask(__name__)

data = {
    "experience": [
        Experience("Software Developer", "A Cool Company", "October 2022", "Present", "Writing Python Code", "example-logo.png")
    ],
    "education": [
        Education("Computer Science", "University of Tech", "September 2019", "July 2022", "80%", "example-logo.png")
    ],
    "skill": [
        Skill("Python", "1-2 Years", "example-logo.png")
    ]
}


@app.route('/test')
def hello_world():
    '''
    Returns a JSON test message
    '''
    return jsonify({"message": "Hello, World!"})


@app.route('/resume/experience', methods=['GET', 'POST'])
def experience():
    '''
    Handle experience requests
    '''
    if request.method == 'GET':
        return jsonify([exp.__dict__ for exp in data['experience']])

    if request.method == 'POST':
        req_data = request.get_json()
        new_experience = Experience(
            req_data['title'],
            req_data['company'],
            req_data['start_date'],
            req_data['end_date'],
            req_data['description'],
            req_data['logo']
        )
        data['experience'].append(new_experience)
        return jsonify({"message": "Experience added successfully!"}), 201


@app.route('/resume/education', methods=['GET', 'POST'])
def education():
    '''
    Handles education requests
    '''
    if request.method == 'GET':
        return jsonify([edu.__dict__ for edu in data['education']])

    if request.method == 'POST':
        req_data = request.get_json()
        new_education = Education(
            req_data['course'],
            req_data['school'],
            req_data['start_date'],
            req_data['end_date'],
            req_data['grade'],
            req_data['logo']
        )
        data['education'].append(new_education)
        return jsonify({"message": "Education added successfully!"}), 201


@app.route('/resume/skill', methods=['GET', 'POST'])
def skill():
    '''
    Handles skill requests
    '''
    if request.method == 'GET':
        return jsonify([sk.__dict__ for sk in data['skill']])

    if request.method == 'POST':
        req_data = request.get_json()
        new_skill = Skill(
            req_data['name'],
            req_data['proficiency'],
            req_data['logo']
        )
        data['skill'].append(new_skill)
        return jsonify({"message": "Skill added successfully!"}), 201


if __name__ == '__main__':
    app.run(debug=True)

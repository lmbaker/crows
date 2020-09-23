from flask import Flask, request

from questionAnswering.SrdResponder import SrdResponder

app = Flask(__name__)

# To start the server:
#     export FLASK_APP=main.py
#     flask run
# Optionally, flask run --host=0.0.0.0 to access this on other devices on the
# network.

# Visit http://127.0.0.1:5000/form-question to enter a question on-screen.
# Send a query to json-question, like this:
# curl --location --request POST 'http://127.0.0.1:5000/json-question' \
# --header 'Content-Type: application/json' \
# --data-raw '{"question": "How tall is a halfling?"}'

srdResponder = SrdResponder()

def answer_question(question_text):
    return srdResponder.top_answer_in_context(question_text)


quick_template = '''Question: {}</br>
                  Answers:</br>{}'''


@app.route('/<string:greeting>')
def hello_world(greeting):
    return 'Hello, World!' + '\n' + greeting


@app.route('/form-question', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':
        # The form has been submitted.
        question = request.form.get('question')
        answer = answer_question(question)

        return quick_template.format(question, answer)

    return '''<form method="POST">
                  Question: <input type="text" name="question"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/json-question', methods=['POST'])
def json_example():
    request_data = request.get_json()

    question = request_data['question']
    answer = answer_question(question)

    return {'question': question,
            'answer': answer}

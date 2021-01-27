from flask import Flask, Markup, render_template, request

from questionAnswering.SrdResponder import SrdResponder, SrdResponderConfig

app = Flask(__name__)

# To start the server:
#     export FLASK_APP=main.py
#     flask run
# Optionally, flask run --host=0.0.0.0 to access this on other devices on the
# network.

# Visit http://127.0.0.1:5000/form-question to enter a question on-screen.
# Send a query to json-question, like this:
'''
curl --location --request POST 'http://127.0.0.1:5000/json-question' \
--header 'Content-Type: application/json' \
--data-raw '{"question": "How tall is a halfling?"}'

or, curl --location --request POST 'http://127.0.0.1:5000/json-all-answers
'''

#config = SrdResponderConfig(retriever='DensePassage')
config = SrdResponderConfig(retriever='Elasticsearch')
srdResponder = SrdResponder(config)


def answer_question(question_text, answer_type='top_5_answer'):
    if answer_type == 'all_answers':
        return srdResponder.answers_with_metadata(question_text)
    elif answer_type == 'top_answer':
        return srdResponder.top_answer_in_context(question_text)
    elif answer_type == 'top_5_answer':
        return srdResponder.top_answer_in_context(question_text, top_5=True)
    else:
        raise ValueError("Unrecognized answer_type '{}'.".format(answer_type))

def answer_question_with_metadata(question_text):
    return srdResponder.full_prediction_output(question_text)


quick_template = '''Question: {}</br>
                  Answers:</br>{}'''


@app.route('/form-question', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':
        # The form has been submitted.
        question = request.form.get('question')
        answer = answer_question(question)

        return render_template("index.html", answer=Markup(answer))
    return render_template("index.html", answer='')


def json_route_helper(request, answer_mode: str):
    request_data = request.get_json()

    question = request_data['question']
    answer = answer_question(question, answer_type = answer_mode)
    return answer


@app.route('/json-question', methods=['POST'])
def json_example():
    request_data = request.get_json()
    question = request_data['question']
    answer = json_route_helper(request, 'top_answer')

    return {'question': question,
            'answer': answer}


@app.route('/json-all-answers', methods=['POST'])
def json_all_answers():
    answer = json_route_helper(request, 'all_answers')
    return answer


@app.route('/json-answers-in-context', methods=['POST'])
def json_answers_in_context():
    request_data = request.get_json()
    question = request_data['question']
    answer = answer_question(question, answer_type = 'top_5_answer')
    return answer


@app.route('/answer-with-metadata', methods=['POST'])
def answer_with_metadata():
    request_data = request.get_json()

    question = request_data['question']
    answer = answer_question_with_metadata(question)

    return answer.as_dict()

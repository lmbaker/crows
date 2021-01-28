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
#config = SrdResponderConfig(retriever='Elasticsearch')
#srdResponder = SrdResponder(config)


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
        #answer = answer_question(question)

        answer = "<br/><br/>Answer 1, from article <i>Gnome</i>:<br/>sters among them are more playful than vicious. Size. Gnomes are <b>between 3 and 4 feet</b> tall and average about 40 pounds. Your size is Small. Speed. You<br/><br/>Answer 2, from article <i>Reincarnate</i>:<br/> 25 Elf, dark 26 – 34 Elf, high 35 – 42 Elf, wood 43 – 46 Gnome, forest <b>47 – 52</b> Gnome, rock 53 – 56 Half-elf 57 – 60 Half-orc 61 – 68 Halfling, lightf<br/><br/>Answer 3, from article <i>Gnome, Deep (Svirfneblin)</i>:<br/> , disguise self Actions War Pick. Melee Weapon Attack: +4 to hit, reach <b>5 ft</b>., one target. Hit: 6 (1d8 + 2) piercing damage. Poisoned Dart. Ranged We<br/><br/>Answer 4, from article <i>Sleet Storm</i>:<br/> up to 1 minute Until the spell ends, freezing rain and sleet fall in a <b>20-foot</b>-tall cylinder with a 40-foot radius centered on a point you choose wit<br/><br/>Answer 5, from article <i>Passwall</i>:<br/>r the duration. You choose the opening’s dimensions: up to 5 feet wide, <b>8 feet</b> tall, and 20 feet deep. The passage creates no instability in a structu"

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

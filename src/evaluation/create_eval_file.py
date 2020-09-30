import json
import os
import requests
from time import time

from evaluation.config import benchmark_filename
from evaluation.config import data_filepath
from evaluation.create_benchmark import fix_filename

# From the path to and name of the json file holding a SQuAD dataset,
# create a list of (question, question-id) tuples.
# List[Tuple[str, int]]

with open(os.path.join(data_filepath, benchmark_filename)) as f:
    squad_benchmark = json.load(f)

question_id_pairs = []
for article in squad_benchmark['data']:
    for para in article['paragraphs']:
        for qas in para['qas']:
            question_id_pairs.append((qas['question'], qas['id']))

# curl --location --request POST  \
# --header 'Content-Type: application/json' \
# --data-raw '{"question": "How tall is a halfling?"}'

predictions_dict = {}

API_ENDPOINT = 'http://127.0.0.1:5000/json-question'

start_time = time()

for question_pair in question_id_pairs[0:2]:
    data = {'question': question_pair[0]}
    r = requests.post(url = API_ENDPOINT, json = data)

    # Get the response JSON, and take the answer (bolded) out of the context.
    ans = r.json()['answer']
    ans = ans.split('<b>')[1].split('</b>')[0]

    predictions_dict[question_pair[1]] = ans

duration = time() - start_time

timing_msg = ('Answering benchmark questions took {:.2f} seconds, '
              'or {:.2f} hours.')
print(timing_msg.format(duration, duration/3600))

predictions_filename = os.path.join(data_filepath,
                                    fix_filename(data_filepath,
                                                 'benchmark_predictions.json'))

with open(predictions_filename, 'w') as f:
    json.dump(predictions_dict, f)

print("Benchmark answers written to: '{}'".format(predictions_filename))

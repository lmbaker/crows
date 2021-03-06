import json
import os
import requests
from time import time
from tqdm import tqdm

from evaluation.config import benchmark_filename
from evaluation.config import data_filepath
from evaluation.create_benchmark import fix_filename
from questionAnswering.utils import create_absolute_path

def get_questions_from_squad(benchmark_filepath, with_answers=False):
    '''From the path to and name of the json file holding a SQuAD dataset,
    create a list of (question, question-id) tuples.

    benchmark_filepath: str A filepath to the SQuAD benchmark file.
    return: List[Tuple[str, int]]
    '''

    with open(benchmark_filepath) as f:
        squad_benchmark = json.load(f)

    question_id_pairs = []
    for article in squad_benchmark['data']:
        for para in article['paragraphs']:
            for qas in para['qas']:
                if with_answers:
                    question_id_pairs.append((qas['question'], qas['id'], [x['answer_text'] for x in qas['answers']]))
                else:
                    question_id_pairs.append((qas['question'], qas['id']))
    return question_id_pairs

def main():

    abs_data_filepath = create_absolute_path(
        os.path.dirname(__file__), data_filepath)

    question_id_pairs = get_questions_from_squad(
        os.path.join(abs_data_filepath, benchmark_filename))


    # curl --location --request POST  \
    # --header 'Content-Type: application/json' \
    # --data-raw '{"question": "How tall is a halfling?"}'

    predictions_dict = {}

    API_ENDPOINT = 'http://127.0.0.1:5000/answer-with-metadata'
    #API_ENDPOINT = 'http://127.0.0.1:5000/json-all-answers'

    start_time = time()

    for question_pair in tqdm(question_id_pairs):
        data = {'question': question_pair[0]}
        r = requests.post(url = API_ENDPOINT, json = data)
        ans = r.json()
        predictions_dict[question_pair[1]] = ans

    duration = time() - start_time

    timing_msg = ('Answering benchmark questions took {:.2f} seconds, '
                  'or {:.2f} hours.')
    print(timing_msg.format(duration, duration/3600))

    predictions_filename = os.path.join(abs_data_filepath,
                                        fix_filename(abs_data_filepath,
                                                     'benchmark_predictions.json'))

    with open(predictions_filename, 'w') as f:
        json.dump(predictions_dict, f)

    print("Benchmark answers written to: '{}'".format(predictions_filename))

if __name__ == '__main__':
    main()

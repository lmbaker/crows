import json
import os

from evaluation.config import data_filepath, benchmark_filename
from evaluation.create_eval_file import get_questions_from_squad
from prediction.prediction_format import PredictionOutput
from questionAnswering.utils import create_absolute_path

# Make a dict where the keys are questions (as question text) and the values
# are the answers. Since the SQuAD eval script saves answers matched to
# question hashes, this is a nice utility script to have.

abs_data_filepath = create_absolute_path(
    os.path.dirname(__file__), data_filepath)

question_id_pairs = get_questions_from_squad(
    os.path.join(abs_data_filepath, benchmark_filename),
    with_answers=True)

question_answer_dict = {}

with open(os.path.join(abs_data_filepath, 'benchmark_predictions_model_roberta-base-squad2-v2.json')) as f:
    id_answer_pairs = json.load(f)

for qid_pair in question_id_pairs:
    question_answer_dict[qid_pair[0]] = {'gold_answers': qid_pair[2],
                                         'predict_output': id_answer_pairs.get(qid_pair[1], '')}

for k,v in question_answer_dict.items():
    print('Question: {}'.format(k))
    print('Benchmark answer(s): {}'.format(v['gold_answers']))
    pred_output = PredictionOutput(**v['predict_output'])
    for i, ans in enumerate(pred_output.answers):
        print('Answer {}: {}'.format(i+1, ans.get_answer()))
    print('')

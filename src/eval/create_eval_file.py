import json
import os
import requests

# Copied from benchmarking code
def fix_filename(file_dir, filename):
    '''Make the given filename unique in the directory by adding a suffix if
    needed. Made to avoid overwriting files.

    file_dir: str
    filename: str, should end with a file extension.
    return: str
    '''
    if '.' not in filename:
        msg = ("Expected the filename to contain a '.' to show a file"
               "extension, got '{}'.")
        raise ValueError(msg.format(filename))
    filename_parts = filename.split('.')
    filename_no_extension = '.'.join(filename_parts[:-1])
    file_extension = '.' + filename_parts[-1]
    if not os.path.exists(os.path.join(file_dir, filename)):
        return filename
    unique_suffix = 1
    while os.path.exists(os.path.join(file_dir,
                                      (filename_no_extension +
                                       str(unique_suffix) +
                                       file_extension))):
        unique_suffix += 1
    return filename_no_extension + str(unique_suffix) + file_extension


# From the path to and name of the json file holding a SQuAD dataset,
# create a list of (question, question-id) tuples.
# List[Tuple[str, int]]

documents_dir = '../../data/documents-dd2e8b2'
benchmark_file = 'benchmark.json'

with open(os.path.join(documents_dir, benchmark_file)) as f:
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

for question_pair in question_id_pairs:
    data = {'question': question_pair[0]}
    r = requests.post(url = API_ENDPOINT, json = data)

    # Get the response JSON, and take the answer (bolded) out of the context.
    ans = r.json()['answer']
    ans = ans.split('<b>')[1].split('</b>')[0]

    predictions_dict[question_pair[1]] = ans

with open(os.path.join(documents_dir, fix_filename(documents_dir, 'benchmark_predictions.json')), 'w') as f:
    json.dump(predictions_dict, f)

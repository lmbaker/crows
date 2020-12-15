import os
from evaluation.config import data_filepath

generated_srd_filepath = os.path.join(data_filepath, 'srd_articles.json')

# Tuple, first argument is the model name or filepath, and second argument
# is a boolean for whether the model references a local file.
model_name_or_path = ('models/roberta-base-squad2-v2', True)
#model_name_or_path = ('deepset/roberta-base-squad2', False)

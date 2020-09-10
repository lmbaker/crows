import json
import os

from svgParsing.parse_rules import generate_srd_articles

#TODO move absolute path to a config file
data_dir = '/home/lauren/dndtep/srdAnswer/data'

if not os.path.exists(os.path.join(data_dir, 'generated')):
    os.makedirs(os.path.join(data_dir, 'generated'))

article_filename = os.path.join(data_dir, 'generated', 'srd_articles.json')

if not os.path.exists(article_filename):
    articles = generate_srd_articles()
    with open(article_filename, 'w') as f:
        json.dump(articles, f)
    print('Created article file!')

else:
    print('Article data file already exists.')

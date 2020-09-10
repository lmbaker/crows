from setuptools import setup, find_packages

print(find_packages(where='src'))

setup(name='srdAnswer',
      version='0.1',
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      scripts=['bin/generate_articles.py'],
      #package_data={'capitalize': ['data/cap_data.txt']},
      )

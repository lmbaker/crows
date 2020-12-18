from setuptools import setup, find_packages

setup(name='srdAnswer',
      version='0.1',
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      scripts=['bin/generate_articles.py'],
      install_requires=[
          'flask',
          'farm-haystack==0.5.0',
      ]
      )

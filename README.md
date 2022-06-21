# Question Answering for Tabletop Game Rules

This repository has tools for answering questions about the content for the fifth edition of the world's first tabletop RPG that has been released under the Open Gaming License.

<!-- To test this out online, visit <website>. (NB: This is a small server, and can only handle a few requests at a time.) -->

To try this out on your machine, clone the repository and follow these steps:

```bash
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.6.2
sudo apt-get install virtualenv
virtualenv srdenv --python python3.7
. ./srdenv/bin/activate
cd flaskapp
export FLASK_APP=main.py
flask run
```

from haystack import Finder
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.reader.farm import FARMReader
from haystack.retriever.sparse import ElasticsearchRetriever
import json

from prediction.prediction_format import PredictionOutput
from questionAnswering.config import generated_srd_filepath
from questionAnswering.utils import make_substring_bold


class SrdResponder:
    '''A class to wrap around the Haystack stack, and provide answers to
    questions with any desired formatting or post-processing.'''

    def __init__(self):

        # Connect to Elasticsearch

        document_store = ElasticsearchDocumentStore(host="localhost",
                                                    username="",
                                                    password="",
                                                    index="document")

        print("Importing documents from '{}'.".format(generated_srd_filepath))
        # Get documents with knowledge

        with open(generated_srd_filepath) as f:
            docs = json.load(f)

        formatted_dicts = [{"name": k, "text": v} for k, v in docs.items()]
        document_store.write_documents(formatted_dicts)

        retriever = ElasticsearchRetriever(document_store=document_store)

        reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2",
                            use_gpu=True)

        self.finder = Finder(reader, retriever)

    def _make_prediction(self, question):
        '''A helper function to call the finder and return answers.

        question: str A question, plaintext.
        return: A dictionary with answers and metadata.
        '''

        return self.finder.get_answers(question=question,
                                       top_k_retriever=10,
                                       top_k_reader=5)

    def top_answer_in_context(self, question: str) -> str:
        '''Return the most likely answer for the given question. Return the
        context, but put the answer in bold.

        question: str representing a question to answer.
        return: str representing the answer.
        '''

        prediction = self._make_prediction(question)
        top_answer_dict = prediction['answers'][0]
        top_answer_text = top_answer_dict['answer']
        top_answer_context = top_answer_dict['context']

        return make_substring_bold(top_answer_context, top_answer_text)

    def answers_with_metadata(self, question):
        '''Return all answer candidates, with metadata, as provided by the
        finder.

        question: str A question, plaintext.
        return: Dict The answer structure as returned by the finder.
        '''

        prediction = self._make_prediction(question)
        return prediction

    def full_prediction_output(self, question: str) -> PredictionOutput:
        '''Return all output from the finder.'''

        prediction = self._make_prediction(question)
        return PredictionOutput(**prediction)

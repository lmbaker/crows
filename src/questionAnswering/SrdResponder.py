import json
import os

from dataclasses import dataclass
from haystack import Finder
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.reader.farm import FARMReader
from haystack.retriever.dense import DensePassageRetriever
from haystack.retriever.sparse import ElasticsearchRetriever

from prediction.prediction_format import PredictionOutput
from questionAnswering.config import generated_srd_filepath, model_name_or_path
from questionAnswering.utils import create_absolute_path, make_substring_bold


@dataclass
class SrdResponderConfig:

    # The retriever to use. Should be 'Elasticsearch' or 'DensePassage'.
    retriever: str

    def __post_init__(self):
        retrieverOptions = ['Elasticsearch', 'DensePassage']
        if self.retriever not in retrieverOptions:
            errorMsg = "Retriever '{}' not recognized. Must be in {}.".format(
                self.retriever, retrieverOptions)
            raise ValueError(errorMsg)


class SrdResponder:
    '''A class to wrap around the Haystack stack, and provide answers to
    questions with any desired formatting or post-processing.'''

    def __init__(self, config: SrdResponderConfig):

        # Connect to Elasticsearch

        document_store = ElasticsearchDocumentStore(host="localhost",
                                                    username="",
                                                    password="",
                                                    index="document")

        total_docs_in_store = document_store.get_document_count()

        if total_docs_in_store > 0:
            # Use document store as-is.
            print("Using existing document store with {} documents.".format(
                total_docs_in_store))

        else:

            absolute_srd_filepath = create_absolute_path(
                os.path.dirname(__file__), generated_srd_filepath)

            # Get documents with knowledge
            print("Importing documents from '{}'.".format(
                absolute_srd_filepath))

            with open(absolute_srd_filepath) as f:
                docs = json.load(f)

            formatted_dicts = [{"name": k, "text": v} for k, v in docs.items()]
            document_store.write_documents(formatted_dicts)

        if config.retriever == 'Elasticsearch':
            retriever = ElasticsearchRetriever(document_store=document_store)

        elif config.retriever == 'DensePassage':
            retriever = DensePassageRetriever(
                document_store=document_store,
                query_embedding_model=(
                    "facebook/dpr-question_encoder-single-nq-base"),
                passage_embedding_model=(
                    "facebook/dpr-ctx_encoder-single-nq-base"),
                max_seq_len_query=64,
                max_seq_len_passage=256,
                batch_size=16,
                use_gpu=True,
                embed_title=True,
                use_fast_tokenizers=True)

            if total_docs_in_store == 0:
                # Assume that if we are re-using a document store, it has the
                # embeddings we want.
                document_store.update_embeddings(retriever)

        abs_model_name_or_path = model_name_or_path[0]
        if model_name_or_path[1]:
            # The model is described by a local filepath
            abs_model_name_or_path = create_absolute_path(
                os.path.dirname(__file__), model_name_or_path[0])

        reader = FARMReader(model_name_or_path=abs_model_name_or_path,
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

    def top_answer_in_context(self, question: str, top_5: bool = False) -> str:
        '''Return the most likely answer for the given question. Return the
        context, but put the answer in bold.

        question: str representing a question to answer.
        return: str representing the answer.
        '''

        prediction = self._make_prediction(question)
        answer_string = '<p>'

        if not top_5:
            top_answer_dict = prediction['answers'][0]
            top_answer_text = top_answer_dict['answer']
            top_answer_context = top_answer_dict['context']

            answer_string += make_substring_bold(top_answer_context, top_answer_text)
        else:
            answer_string += 'Question: {}'.format(question)
            answer_header_template = ('<br/><br/>Answer {}, '
                                      'from article <i>{}</i>:')
            answers = prediction['answers']
            for i in range(5):
                top_answer_text = answers[i]['answer']
                top_answer_context = answers[i]['context']
                answer_string += answer_header_template.format(
                    i+1, answers[i]['meta']['name'])
                answer_string += '<br/>' + make_substring_bold(
                    top_answer_context, top_answer_text)
        answer_string += '</p>'
        return answer_string

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

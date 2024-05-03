import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.resolve().as_posix())
from chatbot.bot import CyberNewsBot
from chatbot.mongo_client import CustomMongoClient
# from dotenv import load_dotenv
# from trulens_eval.feedback.provider import OpenAI
# from trulens_eval import Feedback
# import numpy as np
# from trulens_eval import Tru
# from trulens_eval.app import App
# load_dotenv("./.env")
# from trulens_eval import TruLlama
# from trulens_eval.feedback import Groundedness
# import pymongo
from chatbot.mongo_client import CustomMongoClient
from chatbot import logger_manager as lm
from config import *

# tru = Tru()
# grounded = Groundedness(groundedness_provider=OpenAI())
# provider = OpenAI()

class TruLensRunner:
    """Class act as an interface between backend and frontend"""
    def __init__(self):
        """Initializing all the class variables"""
        self.custom_mongo_client = CustomMongoClient()
        self.cyber_news_bot = CyberNewsBot()
        self.truelens_logger = lm.initialize_logger("TruLens", TRULENS_LOG_FILE_PATH)
        self.query_engine = self.custom_mongo_client.get_query_engine() #query engine used by both backend and trulens
    
    def get_original_response(self, summary, query):
        """Function to call the backend and get the response to show
        to the user

        Parameters
        ----------
        summary : Previous summary
        query : Input query from user

        Returns
        -------
        Final response from the backend
        """
        return self.cyber_news_bot.get_response_from_llm(summary, query, self.query_engine)

    # def run_trulense(self, query):
    #     """Function for evaluation of trulens

    #     Parameters
    #     ----------
    #     query : Input query from user

    #     Returns
    #     -------
    #     Recordings done by the trulens
    #     """
    #     try:
    #         query_engine = self.query_engine
    #         context = App.select_context(query_engine)

    #         f_groundedness = (
    #             Feedback(grounded.groundedness_measure_with_cot_reasons)
    #             .on(context.collect()) # collect context chunks into a list
    #             .on_output()
    #             .aggregate(grounded.grounded_statements_aggregator)
    #         )
    #         f_context_relevance = (
    #             Feedback(provider.context_relevance_with_cot_reasons)
    #             .on_input()
    #             .on(context)
    #             .aggregate(np.mean)
    #         )
    #         f_answer_relevance = (
    #             Feedback(provider.relevance)
    #             .on_input_output()
    #         )

    #         tru_query_engine_recorder = TruLlama(query_engine, app_id=APP_NAME, feedbacks=[f_groundedness, f_answer_relevance, f_context_relevance])

    #         #initiating trulens recording
    #         with tru_query_engine_recorder as recording:
    #             self.custom_mongo_client.run_query_engine(query_engine, query)
    #         return recording.records

    #     except Exception as e:
    #         self.truelens_logger.error(e)

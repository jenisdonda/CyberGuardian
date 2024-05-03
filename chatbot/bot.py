from config import *
from llama_index.llms.openai import OpenAI
from chatbot.mongo_client import CustomMongoClient
from dotenv import load_dotenv
import chatbot.logger_manager as lm
load_dotenv(ENV_PATH)
import json

class CyberNewsBot:
    def __init__(self):
        """
        Initializes the CyberNewsBot instance by setting up the logger and the MongoDB client.
        """
        self.logger = lm.initialize_logger("Run LLM", RUN_LLM_LOG_FILE_PATH)
        self.mongo_client = CustomMongoClient()

    def get_open_ai_instanace(self):
        """
        Retrieves an instance of the OpenAI class with the specified model and temperature.

        Returns
        -------
        OpenAI: An instance of the OpenAI class with the specified model and temperature.
        """
        return OpenAI(model = OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)

    def merge_vectors_into_string(self, all_vectors):
        """
        Merges a list of vectors into a single string.

        Parameters
        ----------
        all_vectors: list
            A list of vectors to be merged into a string.

        Returns
        -------
        str
            The merged string containing all the vectors.
        """
        result = ""
        for vector in all_vectors:
            result += vector + "\n"
        return result

    def format_memory(self, summary):
        """
        A function that formats memory.

        Parameters
        ----------
        summary: Any
            The summary to be formatted.

        Returns
        -------
        Any
            The formatted memory.
        """
        return summary

    def parse_into_json(self, response):
        """
        Parses a JSON object from the given response string.

        Parameters
        ----------
        response: str
            The response string containing the JSON object.

        Returns
        -------
        dict
            The parsed JSON object as a dictionary.
        """
        start_index = response.find("{")
        end_index = response.rfind("}")
        if start_index > end_index:
            return {}
        return json.loads(response[start_index:end_index + 1])

    def generate_summary(self, previous_summary, user_question, bot_response, llm):
        """
        Generates a summary based on the previous summary, user question, bot response, and the language model.

        Parameters
        ----------
        previous_summary: Any
            The previous summary to be included in the generated summary.
        user_question: Any
            The user question to be included in the generated summary.
        bot_response: Any
            The bot response to be included in the generated summary.
        llm: Any
            The language model used to generate the summary.

        Returns
        -------
        Any
            The generated summary.
        """
        return llm.complete(SUMMARY_PROMPT.format(previous_summary, user_question, bot_response))

    def get_response_from_llm(self, summary, input_prompt, query_engine):
        """
        Retrieves a response from a language model based on the provided summary and input prompt.

        Parameters
        ----------
        summary: Any
            The summary information to be used in obtaining the response.
        input_prompt: Any
            The input prompt for the language model.

        Returns
        -------
        Any
            The response generated by the language model based on the input.

        Raises
        ------
        Exception
            If an error occurs during the process, it is logged.
        """
        try:
            self.logger.info("Starting RAG approach in MongoDB")
            nearest_vector, all_urls = self.mongo_client.use_mongo_rag(input_prompt, query_engine)

            self.logger.info("Merging vectors")
            complete_context = self.merge_vectors_into_string(nearest_vector)
            
            self.logger.info("Formatting memory")
            memory = self.format_memory(summary)
            
            llm = self.get_open_ai_instanace()
            self.logger.info("Running LLM")
            
            response = llm.complete(MAIN_PROMPT.format(memory, input_prompt, complete_context))
           
            response = self.parse_into_json(str(response))
            response["all_urls"] = all_urls
            response["summary"] = str(self.generate_summary(summary, input_prompt, response["response"], llm))
            
            return response
        
        except Exception as e:
            self.logger.error(e)
            raise e
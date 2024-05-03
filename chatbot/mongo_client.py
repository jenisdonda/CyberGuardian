# from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.llms.together import TogetherLLM
import pymongo
from llama_index.core.settings import Settings
from llama_index.core import Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from config import *
from chatbot import logger_manager as lm
from llama_index.core.node_parser import SentenceSplitter
node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

def singleton(cls):
    """
    A function that implements the singleton design pattern to ensure only one instance of a class is created.
    
    Parameters:
    cls: class
        The class for which the singleton pattern is being applied.
    
    Returns:
    function
        The singleton instance of the class.
    """
    all_cls = {}
    def get_instance(*args, **kwargs):
        if cls not in all_cls:
            all_cls[cls] = cls(*args, **kwargs)
        return all_cls[cls]
    return get_instance

@singleton
class CustomMongoClient:
    def __init__(self):
        """Initializing mongo instance and also setting OpenAI model for llama_index"""
        self.embed_model = TogetherEmbedding(model_name=TOGETHER_AI_EMBEDDING_MODEL, dimensions=EMBEDDING_MODEL_DIMENSIONS)
        Settings.llm = TogetherLLM(model=TOGETHER_AI_MODEL)
        Settings.embed_model = self.embed_model
        
        self.mongo_db_logger = lm.initialize_logger("Mongo DB", MONGO_DB_LOG_FILE_PATH)
        self.mongo_instance = self.get_mongo_instance()

    def get_mongo_instance(self):
        """Function to get MongoDB instance

        Returns
        -------
        Mongo DB Instance
        """
        try:
            mongo_client = pymongo.MongoClient(MONGO_URI)
            return MongoDBAtlasVectorSearch(mongo_client, index_name=INDEX_NAME, db_name=DB_NAME, collection_name=COLLECTION_NAME)
        except Exception as err:
            self.mongo_db_logger.error(err)
            raise Exception("Error while connecting MongoDB")

    def store_in_vector_db(self, all_text):
        """Function to store list of texts in vector database

        Parameters
        ----------
        all_text : list[str]
        """
        try:
            self.mongo_db_logger.info("Storing {0} in mongo db".format(len(all_text)))
            store = self.mongo_instance
            documents = [Document(text = t["summary"], 
                                  metadata = {"url": t["url"]}) for t in all_text]
            node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            documents = node_parser.get_nodes_from_documents(
            documents, show_progress=False
            )
            for document in documents:
                document.embedding = self.embed_model.get_text_embedding(
                    document.get_content(metadata_mode="all")
                )
            store.add(documents)
            self.mongo_db_logger.info("Data stored in vector db")
        except Exception as err:
            self.mongo_db_logger.error(err)
            raise Exception("Error while storing data in vector db")

    def get_query_engine(self):
        """Function to get the query engine

        Returns
        -------
        Mongo DB query_engine
        """
        store = self.mongo_instance
        index = VectorStoreIndex.from_vector_store(store)

        self.mongo_db_logger.info("Starting index query engine")
        return index.as_query_engine()

    def run_query_engine(self, query_engine, input_prompt):
        """Function to run the query engine

        Parameters
        ----------
        query_engine : Mongo DB Query Engine
        input_prompt : Input prompt for the query
        """
        return query_engine.query(RAG_QUERY.format(input_prompt))

    def use_mongo_rag(self, input_prompt, query_engine):
        """Function to use RAG approach to search for nearest vectors in the db.

        Parameters
        ----------
        input_prompt : Question that user typed

        Returns
        -------
        Vector of string which consists of text of nearest vectors in db.
        """
        try:
            self.mongo_db_logger.info("Starting RAG query engine")
            response = self.run_query_engine(query_engine, input_prompt)
            self.mongo_db_logger.info("RAG query engine completed")
           
            result = []
            all_urls = set()
            
            for each_response in response.source_nodes:
                result.append(each_response.text)
                all_urls.add(each_response.metadata["url"])         
            return result, list(all_urls)
        
        except Exception as err:
            self.mongo_db_logger.error(err)
            raise Exception("Error while using RAG approach")
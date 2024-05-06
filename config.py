from pathlib import Path
import os

CURRENT_DIRECTORY = Path(__file__).parent.resolve()
APP_NAME="CyberGuardian"
TOGETHER_AI_MODEL = "meta-llama/Llama-3-70b-chat-hf"
TOGETHER_AI_EMBEDDING_MODEL = "togethercomputer/m2-bert-80M-8k-retrieval"
RESCHEDULE_HOURS = 1
STATE_FILE_PATH = Path.joinpath(CURRENT_DIRECTORY, "data/state.json")
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@cluster1.nyahtop.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
INDEX_NAME = "vector_index"
DB_NAME = "cyber_news_db"
COLLECTION_NAME = "cyber_news_collection2"
RUN_LLM_LOG_FILE_PATH = Path.joinpath(CURRENT_DIRECTORY, "logs/run_llm.log")
MONGO_DB_LOG_FILE_PATH = Path.joinpath(CURRENT_DIRECTORY, "logs/mongo_client.log")
SCHEDULAR_LOG_PATH = Path.joinpath(CURRENT_DIRECTORY, "logs/scheduling.log")
FRONTEND_LOG_PATH = Path.joinpath(CURRENT_DIRECTORY, "logs/frontend_logs.log")
START_RUN = {"dateTime": "2024-04-29T05:20:32Z"}
NEWS_API_URL="https://eventregistry.org/api/v1/article/getArticles"
NO_OF_ARTICLES_PER_PAGE = 100
ARTICLE_TYPES = ["news", "blog"]
ARTICLE_KEYWORDS = [
    "Cybersecurity",
    "Information security," "Network security",
    "Data protection",
    "Cyber threats",
    "Cyber attacks",
    "Firewall",
    "Intrusion detection",
]

MAIN_PROMPT = """
Consider yourself as an expert cyber security advisor.\n
Consider this message history:\n
{0}
\n
Current Question: {1}\n
Cyber security information: {2}\n
The response should be only in the JSON format.\n
You should compulsory follow the following json formate:\n
"response": "Answer the current question"\n
"follow_up_question": ["Follow up question1 based on the current responses and previous responses",
"Follow up question1 based on the current responses and previous responses"...]\n
There should be compulsory "response" and "follow_up_question" keys only in your JSON response.\n
If follow up question is not required for current question, then just make it an empty array.
"""

EMBEDDING_MODEL_DIMENSIONS = 256
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 0
RAG_QUERY = "Give the information related to the following question: \n{0}"
MEMORY_WINDOW_SIZE = 20

SUMMARY_PROMPT = """
Consider yourself as an expert cyber security advisor.\n
Here is the summary of previous question and answer related to cyber security that user has asked you and you replied:
{0}\n
Now, user asked you the following question:\n
{1}\n
You replied it as the following answer:\n
{2}\n
I want you to generate the combined summary of all your responses so that after reading your final summary everyone can easily understand.\n
Try to keep the summary aligned with cyber security domain.\n
The summary should be as detailed as possible.\n
Give me summary in detailed paragraph.\n
Your summary should also contains user questions and answers.\n
Lets go step by step.
\n"""
TRULENS_LOG_FILE_PATH = Path.joinpath(CURRENT_DIRECTORY, "logs/truelens_logs.log")
ENV_PATH = Path.joinpath(CURRENT_DIRECTORY, ".env")
LOGO_PATH = os.path.join(os.getcwd(), "assets/logo.png")
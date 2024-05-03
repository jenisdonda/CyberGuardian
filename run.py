from chatbot.bot import CyberNewsBot
from dotenv import load_dotenv

load_dotenv("./.env")

if __name__ == "__main__":
    print(
        CyberNewsBot().get_response_from_llm(
            "", "What are the latest news related to the cyber security?"
        )
    )

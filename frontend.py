import streamlit as st
from trulens_runner import TruLensRunner
from chatbot import logger_manager as lm
from config import *

frontend_logger=lm.initialize_logger("Frontend", FRONTEND_LOG_PATH)

class Message:
    actor: str
    payload: str
    reference_links: list[str]
    follow_up_questions: list[str]
    status: str

    def __init__(self, actor, payload, status, reference_links, follow_up_questions):
        """
        Initializes a Message object with the provided parameters.

        Parameters:
            actor (str): The actor of the message.
            payload (str): The main content of the message.
            status (str): The status of the message.
            reference_links (list[str]): A list of reference links related to the message.
            follow_up_questions (list[str]): A list of follow-up questions based on the message.

        Returns:
            None
        """
        self.actor = actor
        self.payload = payload
        self.status = status
        self.reference_links = reference_links
        self.follow_up_questions = follow_up_questions

USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"
MESSAGE = "message"
SUMMARY = "summary"

def get_llm_chain_from_session():
    return st.session_state["llm_chain"]

if MESSAGE not in st.session_state:
    st.session_state[MESSAGE] = [{"user": Message(actor = USER, payload = "", status = "done", reference_links = [], follow_up_questions = []), "ai": Message(actor = ASSISTANT, status = "done", payload = "How can I help You?", reference_links = [], follow_up_questions = [])}]

if SUMMARY not in st.session_state:
    st.session_state[SUMMARY] = ""

st.image(LOGO_PATH, width=70) 
st.title('CyberGuardian ')

prompt: str = st.chat_input("Enter a prompt here")
bot = TruLensRunner()

if MESSAGE in st.session_state:
    for message_pair in st.session_state[MESSAGE]:
        if len(message_pair[USER].payload):
            st.chat_message(USER).write(message_pair[USER].payload)
        combined_message = message_pair[ASSISTANT].payload
        
        #Showing beautiful response
        if message_pair[ASSISTANT].follow_up_questions:
            combined_message += "\n\nFollow-up Questions:\n- " + "\n- ".join(message_pair[ASSISTANT].follow_up_questions)

        if message_pair[ASSISTANT].reference_links:
            combined_message += "\n\nReference Links:\n- " + "\n- ".join(message_pair[ASSISTANT].reference_links)
            
        st.chat_message(ASSISTANT).write(combined_message)

if prompt:
    frontend_logger.info("User input: " + prompt)
    st.session_state[MESSAGE].append({"user": Message(actor=USER, payload=prompt, status="done", reference_links=[], follow_up_questions=[]), "ai": Message(actor=ASSISTANT, status = "pending", payload="", reference_links=[], follow_up_questions=[])})
    st.chat_message(USER).write(st.session_state[MESSAGE][-1][USER].payload)

    with st.spinner("Please wait.."):
        try:
            response = bot.get_original_response(st.session_state[SUMMARY], prompt) # First getting original response
        except Exception as e:
            frontend_logger.error("Exception in original response: {0}".format(e))
            response = None
        try:
            trulense_records = bot.run_trulense(prompt) # Running trulens recorder
        except Exception as e:
            frontend_logger.error("Error in trulense: {0}".format(e))
        
        if response is None:
            frontend_logger.info("No response from LLM")
            response = {"response": "Sorry, I am unable to answer that. Please try again.","follow_up_question":[],"all_urls":[]}
        else:
            combined_message = response["response"]
            frontend_logger.info("Response arrived from prompt: " + prompt)

            if response["follow_up_question"]:
                combined_message += "\n\nFollow-up Questions:\n- " + "\n- ".join(response["follow_up_question"])
            if response["all_urls"]:
                combined_message += "\n\nReference Links:\n- " + "\n- ".join(response["all_urls"])

            st.session_state[MESSAGE][-1][ASSISTANT] = Message(actor=ASSISTANT, payload=response["response"], follow_up_questions=response["follow_up_question"], reference_links=response["all_urls"], status="done")
            st.chat_message(ASSISTANT).write(combined_message)

            if response.get(SUMMARY) is not None:
                frontend_logger.info("Summary came from prompt: " + prompt)
                st.session_state[SUMMARY] = response.get(SUMMARY)

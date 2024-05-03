
# CyberGuardian

This project is about Cyber security domain based Chatbot.
# 
Which is used for getting latest news or blog article regarding to cyber security, cyber attacks, vulnerabilities and many more.
>
 We use below tools/technologies in this project:
> 
* **Llamaindex** : LlamaIndex is foundational for use cases involving the Retrieval Augmented Generation (RAG) of information.

* **mongoDB** : Used for storing embeddings vectors.

* **GPT-4** : it is used for geeting response for user query. and it takes context from mongoDB relevant vectores so we can get real time information.

* **Trulens** : TruLens is a powerful open source library for evaluating and tracking large language model-based applications. TruLens provides a set of tools for developing and monitoring neural nets, including large language models (LLMs).

* **Streamlit** : Streamlit is a promising open-source Python library, which enables developers to build attractive user interfaces in no time. 


#
**Steps to run the application :** 

First,
You have to create cluster in mongoDB and make collection and index in it. and then you have to specify the following in config.py file:

*MONGO_URI*

*DB_NAME*

*COLLECTION_NAME*

*INDEX_NAME*

#
For request to OpenAI LLM and news api you have provide following in .env file.

*OPENAI_API_KEY*

*NEWS_API_KEY*

You can find news api key here : https://newsapi.ai/ 

#
First you have to install all dependencies :
```console
$ pip install -r requirement.txt
```
>
Run the scheduler for API :
```console
$ python chatbot/scheduler.py
```
>
Run Trulens Dashboard :
```console
$ trulens-eval
```
>
Run Frontend :
```console
$ streamlit run frontend.py
```

Now your chatbot running fine. with following all the above steps.






 



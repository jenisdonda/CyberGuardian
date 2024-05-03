"""in this file we have to make schedular api requests whcih take response from api in every 1 hour and add it in current list"""

import requests
import schedule
import time
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent.resolve().as_posix())
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from config import *
from chatbot.mongo_client import CustomMongoClient
load_dotenv()
from chatbot import logger_manager as lm


class Schedular_API:
    def __init__(self, state_file_path):
        """
        Initializes the Schedular_API object with the state file path and initializes the logger.
        
        Parameters:
            state_file_path (str): The path to the state file.
        
        Returns:
            None
        """
        self.state_file_link = state_file_path
        self.logger = lm.initialize_logger("Schedular Logs", SCHEDULAR_LOG_PATH)

    def fetch_data_from_api(self, page, date):
        """
        Fetches data from the API based on the provided page and date.

        Parameters:
            page (int): The page number for the API request.
            date (str): The date for the API request.

        Returns:
            dict: The response data from the API request.
        """
        try:
            body = {
                "action": "getArticles",
                "keyword": ARTICLE_KEYWORDS,
                "keywordOper": "or",
                "articlesPage": page,
                "articlesCount": NO_OF_ARTICLES_PER_PAGE,
                "lang": ["eng"],
                "articlesSortBy": "date",
                "articlesSortByAsc": "false",
                "articlesArticleBodyLen": -1,
                "resultType": "articles",
                "dataType": ARTICLE_TYPES,
                "apiKey": os.getenv("NEWS_API_KEY"),
                "dateStart": date,
            }

            # Api call
            response = requests.get(NEWS_API_URL, json=body, timeout=5)
            response.raise_for_status()
            
            response_data = response.json()
            return response_data

        except requests.exceptions.HTTPError as e:
            raise e
            
    def last_date_and_time(self):
        """
        Retrieves the last date and time from the state file.

        Returns:
            str: The last date and time stored in the state file.
        """
        try:
            # take the date and time of last news fetched
            with open(self.state_file_link, "r", encoding="utf-8") as outfile:
                last_state = json.load(outfile)
                return last_state["dateTime"]
        except FileNotFoundError as e:
            # if state file not found then assign start date and time
            self.logger.error(e)
            last_state = START_RUN.get("dateTime")
            return last_state
        except json.decoder.JSONDecodeError as e:
            self.logger.error(e)

    def update_to_latest_news_date(self, date_time):
        """
        Writes the latest news date and time to the state file.

        Parameters:
            date_time (str): The date and time to update.

        Returns:
            None
        """
        try:
            # update date and time to latest news fetched
            with open(self.state_file_link, "w", encoding="utf-8") as outfile:
                json.dump(
                    {"dateTime": date_time},
                    outfile,
                )
        except Exception as e:
            self.logger.error(e)

    def fetch_and_store_data(self):
        """
        Fetches and stores data from the API, updates the latest news date and time, and logs the number of responses stored.
        """
        try:
            all_responses = []
            page = 1
            flag = False

            last_news_date_time = self.last_date_and_time()
            last_news_date = last_news_date_time.split("T")[0]

            # first response
            all_articles = self.fetch_data_from_api(page, last_news_date)

            if all_articles and "articles" in all_articles and "results" in all_articles["articles"]:
                self.update_to_latest_news_date(all_articles["articles"]["results"][0]["dateTime"])
            else:
                return []

            # we iterate through all pages while latest news are available
            while not flag and all_articles["articles"]["results"]:
                for article in all_articles["articles"]["results"]:
                    date_time_obj = article["dateTime"]

                    if date_time_obj > last_news_date_time:
                        all_responses.append({"summary":article["body"], "url":article["url"]})
                    else:
                        flag = True
                        break

                page += 1
                all_articles = self.fetch_data_from_api(page, last_news_date)

            if len(all_responses):
                self.logger.info("Storing {0} responses into mongodb".format(len(all_responses)))
                CustomMongoClient().store_in_vector_db(all_responses)
        except Exception as err:
            self.logger.error(err)

def main():
    """
    The main function that schedules a task to fetch and store data every 10 seconds.
    """
    schedule.every(10).minutes.do(Schedular_API(STATE_FILE_PATH).fetch_and_store_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
     main()

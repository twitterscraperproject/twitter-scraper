import os
import json
from dotenv import load_dotenv


class Settings:
    """Settings storage"""

    prefix = 'TWITTER_SCRAPER_'

    session = {
        'storage': ''
    }

    credentials = {
        'login': '',
        'password': ''
    }

    urls = {
        'login': '',
        'advanced_search': ''
    }

    settings = {
        'limit_posts': 0,
        'proxy': '',
        'login_next_button': ''
    }

    writer = {
        'path': '',
        'type': '',
        'spreadsheet_name': '',
        'sharing_email': ''
    }

    def __init__(self):

        load_dotenv()

        self.session['storage'] = os.getenv("{}SESSION_STORAGE".format(self.prefix))

        self.credentials['login'] = os.getenv("{}CREDENTIALS_LOGIN".format(self.prefix))
        self.credentials['password'] = os.getenv("{}CREDENTIALS_PASSWORD".format(self.prefix))
        print(self.credentials['password'])

        self.urls['login'] = os.getenv("{}URLS_LOGIN".format(self.prefix))
        self.urls['advanced_search'] = os.getenv("{}URLS_ADVANCED_SEARCH".format(self.prefix))

        self.settings['category_and_keywords'] = json.loads(os.getenv("{}SETTINGS_CATEGORY_KEYWORDS".format(self.prefix), '{}'))
        self.settings['limit_posts'] = int(os.getenv("{}SETTINGS_LIMIT_POSTS".format(self.prefix)))
        self.settings['proxy'] = os.getenv("{}SETTINGS_PROXY".format(self.prefix))
        self.settings['login_next_button'] = os.getenv("{}SETTINGS_LOGIN_NEXT_BUTTON".format(self.prefix))

        self.writer['path'] = os.getenv("{}WRITER_PATH".format(self.prefix))
        self.writer['type'] = os.getenv("{}WRITER_TYPE".format(self.prefix))
        self.writer['spreadsheet_name'] = os.getenv("{}WRITER_GSNAME".format(self.prefix))
        self.writer['sharing_email'] = os.getenv("{}WRITER_SHARING_EMAIL".format(self.prefix)) 

        self.settings['category_and_adv_search_url'] = self.prepare_advanced_search_params() 


    def prepare_advanced_search_params(self):
        result = {}
        for category, keywords in self.settings['category_and_keywords'].items():
            q_params = "({}) ".format(" OR ".join(keywords))
            q_params += ' lang%3Auk'
            params = {}

            params['f'] = 'top'
            params['q'] = q_params
            params['src'] = 'typed_query'

            params_parts = []
            for param in params:
                params_parts.append("{}={}".format(param, params[param]))

            params_urlencoded = "&".join(params_parts)
            # Combines all the query params for the advanced search
            result[category] = "{}?{}".format(self.urls['advanced_search'], params_urlencoded)
        return result
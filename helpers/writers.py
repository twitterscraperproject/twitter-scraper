import os.path
import csv
import gspread
from gspread.exceptions import SpreadsheetNotFound


class BaseWriter:

    headers = [
        'ID',
        'Account name',
        'Account created on',
        'Tweet text',
        'Tweet views count',
        'Tweet retweet count',
        'Tweet favorite count',
        'Tweet created on',
        'Category'
    ]

    def _process_chunk_data(self, data):
        chunk_data = []
        for id in data:

            item = data[id]

            id = ''
            if('id' in item.keys()):
                id = item['id']

            account_name = ''
            if('account_name' in item.keys()):
                account_name = item['account_name']

            account_created = ''
            if('account_created' in item.keys()):
                account_created = item['account_created']

            text = ''
            if('text' in item.keys()):
                text = item['text']

            views = ''
            if('views' in item.keys()):
                views = item['views']

            retweets = ''
            if('retweets' in item.keys()):
                retweets = item['retweets']

            favorite = ''
            if('favorite' in item.keys()):
                favorite = item['favorite']

            created = ''
            if('created' in item.keys()):
                created = item['created']
            
            chunk_data.append([
                id,
                account_name,
                account_created,
                text,
                views,
                retweets,
                favorite,
                created,
                self.category
            ])
        return chunk_data
        

class CSVWriter(BaseWriter):
    """Writes data to CSV files"""

    def __init__(self, filename, category):
        self.category = category
        self.filename = filename

    def init_document(self):
        if os.path.exists(self.filename):
            return 
        with open(self.filename, 'a', newline='', encoding = 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
    
    def write_chunk(self, data):
        chunk_data =  self._process_chunk_data(data)
        with open(self.filename, 'a', newline='', encoding = 'utf-8') as file:
            writer = csv.writer(file)
            for row in chunk_data:
                writer.writerow(row)
        
    def get_used_tweet_ids(self):
        if not os.path.exists(self.filename):
            return []
        
        used_tweet_ids = []
        with open(self.filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if(row[0] == 'ID'):
                    continue
                used_tweet_ids.append(row[0])
        return used_tweet_ids


class GSWriter(BaseWriter):
    """Writes data to Google Spreadsheet"""

    def __init__(self, spreadsheet_name, category, sharing_email):
        self.spreadsheet_name = spreadsheet_name
        self.category = category
        self.sharing_email = sharing_email

    def init_document(self):
        gc = gspread.service_account(filename='google_credentials.json')

        try:
            sh = gc.open(self.spreadsheet_name)
            self.worksheet = sh.get_worksheet(0)
        except SpreadsheetNotFound:
            sh = gc.create(self.spreadsheet_name)
            sh.share(self.sharing_email, perm_type='user', role='writer')
            self.worksheet = sh.get_worksheet(0)
            self.worksheet.append_row(self.headers)
    
    def write_chunk(self, data):
        chunk_data = self._process_chunk_data(data)
        for row in chunk_data:
            self.worksheet.append_row(row)

    def get_used_tweet_ids(self):
        gc = gspread.service_account(filename='google_credentials.json')

        try:
            sh = gc.open(self.spreadsheet_name)
            worksheet = sh.get_worksheet(0)
            return worksheet.col_values(1)[1:]
        except SpreadsheetNotFound:
            return []
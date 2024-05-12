import datetime


class Parser:
    """Parses the JSON with tweets"""

    added_tweets = 0

    def __init__(self, writer, settings):
        self.writer = writer
        self.settings = settings

        self.used_tweet_ids = writer.get_used_tweet_ids()
        writer.init_document()


    def parse(self, json):

        cur_node = json

        node_paths = [
            'data',
            'search_by_raw_query',
            'search_timeline',
            'timeline',
            'instructions'
        ]

        for node_path in node_paths:
            if(node_path in cur_node.keys()):
                cur_node = cur_node[node_path]
            else:
                return []

        chunk = self.populate_chunk(cur_node)
        self.writer.write_chunk(chunk)
        self.used_tweet_ids.extend([tweet_id for tweet_id in chunk])
        print("New tweets count: {}".format(self.added_tweets))
        print("Total tweets count: {}".format(len(self.used_tweet_ids)))
        return chunk

    def populate_chunk(self, cur_node):
        chunk = {}
        for instruction in cur_node:
            if('entries' in instruction):
                for entry in instruction['entries']:
                    item_content = entry.get('content', {}).get('itemContent', {})
                    # Skip ad tweets
                    if 'promotedMetadata' in item_content:
                        continue
                    tweet_results = item_content.get('tweet_results')
                    if tweet_results:
                        
                        # Parses exact tweet
                        tweet_raw = tweet_results['result']

                        tweet_id = False
                        if('rest_id' in tweet_raw.keys()):
                            tweet_id = tweet_raw['rest_id']

                            if(tweet_id not in self.used_tweet_ids and tweet_id not in chunk.keys()):

                                if(self.added_tweets < self.settings.settings['limit_posts']):
                                    tweet = self.parse_tweet(tweet_raw)
                                    chunk[tweet_id] = tweet
                                    self.added_tweets += 1
                                else:
                                    return chunk
        return chunk

    def parse_tweet(self, data):

        tweet = {
            'id': '',
            'account_name': '',
            'account_created': '',
            'text': '',
            'views': '',
            'retweets': '',
            'favorite': '',
            'created': ''
        }

        if('rest_id' in data.keys()):
            tweet['id'] = data['rest_id']

        if('core' in data.keys()):
            if('user_results' in data['core'].keys()):
                if('result' in data['core']['user_results'].keys()):
                    if('legacy' in data['core']['user_results']['result'].keys()):
                        tweet['account_name'] = data['core']['user_results']['result']['legacy']['name']
                        tweet['account_created'] = self._parse_date(data['core']['user_results']['result']['legacy']['created_at'])
        if('note_tweet' in data.keys()):
            if('note_tweet_results' in data['note_tweet'].keys()):
                if('result' in data['note_tweet']['note_tweet_results'].keys()):
                    if('text' in data['note_tweet']['note_tweet_results']['result'].keys()):
                        tweet['text'] = data['note_tweet']['note_tweet_results']['result']['text']


        if('legacy' in data.keys()):
            if(tweet['text'] == '' and 'full_text' in data['legacy'].keys()):
                tweet['text'] = data['legacy']['full_text']

            if('retweet_count' in data['legacy'].keys()):
                tweet['retweets'] = data['legacy']['retweet_count']

            if('favorite_count' in data['legacy'].keys()):
                tweet['favorite'] = data['legacy']['favorite_count']

            if('created_at' in data['legacy'].keys()):
                tweet['created'] = self._parse_date(data['legacy']['created_at'])



        if('views' in data.keys()):
            if('count' in data['views'].keys()):
                tweet['views'] = data['views']['count']


        return tweet
    
    def _parse_date(self, date_representation):
        return str(datetime.datetime.strptime(date_representation, "%a %b %d %H:%M:%S %z %Y").date())
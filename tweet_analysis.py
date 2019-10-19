# Twitter and API related
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import twitter_credentials
from twitter_handles import usernames, number_of_tweets

# Data manipulation, analysis and visualization
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# NLP
import re
from textblob import TextBlob
from wordcloud import WordCloud
from nltk.corpus import stopwords



# Twitter client
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets



# Twitter authenticator
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth



# Twitter Streamer
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=hash_tag_list)



# Twitter stream listener
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            print("Fetch successful")
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True
          
    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)



# Tweet analyzer
class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    

    def analyze_polarity(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        polarity_score = round(analysis.sentiment.polarity, 2)
        return polarity_score
    

    def analyze_subjectivity(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        subjectivity_score = round(analysis.sentiment.subjectivity, 2)
        return subjectivity_score


    # Creating DataFrame from JSON file extracted.
    def create_df_from_json(self, json_filename):
        """
        Definition:
            Takes in a JSON filename (Eg: 'tweets_politics.json') and returns
            Pandas DataFrame with relevant data.

        Parameters:
            - json_filename (string)

        Returns:
            - Pandas DataFrame containing tweet data.

        """
        # json_filename = 'tweets_politics.json'
        list_of_dicts = list()
        with open(json_filename, 'r') as json_file:
            for json_obj in json_file:
                try:
                    dict_json_obj = json.loads(json_obj)
                    # print(type(dict_json_obj))
                    list_of_dicts.append(dict_json_obj)
                except ValueError as ve:
                    # print("ValueErrorMsg: {}".format(ve))
                    pass

        df_twitter_data = pd.DataFrame(list_of_dicts)
        rename_dict = {
            'text': 'tweets',
            'id': 'id',
            'created_at': 'date',
            'source': 'source',
            'retweet_count': 'retweets',
            'favorite_count': 'likes'
        }
        columns_required = list(rename_dict.values())
        df_twitter_data.rename(rename_dict, axis=1, inplace=True)
        df_twitter_data = df_twitter_data.loc[:, columns_required]
        df_twitter_data['len'] = df_twitter_data['tweets'].apply(len)
        return df_twitter_data


    # Tweets to DataFrame
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['polarity'] = np.array([self.analyze_polarity(tweet.text) for tweet in tweets])
        df['subjectivity'] = np.array([self.analyze_subjectivity(tweet.text) for tweet in tweets])
        return df
    

    def drop_retweets(self, tweet):
        """
        Returns False if tweet is a retweet; returns True otherwise.
        """
        if str(tweet)[:3] == 'RT ':
            return False
        return True
    
    
    def extract_mentions(self, tweet_series):
        mention = re.findall('@[A-Za-z0-9]+', tweet_series)
        return mention

    
    def get_mention_stats(self, df):
        series = df['tweets'].apply(self.extract_mentions)
        series_list = [mention for row in series for mention in row]

        dict_mention_counts = dict()
        for mentioner in series_list:
            if mentioner in dict_mention_counts.keys():
                count = dict_mention_counts[mentioner]
                count += 1
                dict_mention_counts[mentioner] = count
            else:
                dict_mention_counts[mentioner] = 1

        df_mentioned = pd.DataFrame({
            'username': list(dict_mention_counts.keys()),
            'mentions_received': list(dict_mention_counts.values())
        })
        df_mentioned.sort_values(by='mentions_received', ascending=False, inplace=True)
        df_mentioned.reset_index(drop=True, inplace=True)
        return df_mentioned


    def create_plots(self, df_with_sentiment):
        """
        Creates and saves visualizations regarding the sentiment extracted.
        Plots are over a period of time (specified by the dates).
        """
        dates = df_with_sentiment['date']
        step_size = 0.25
        
        plt.figure(figsize = (25, 14))
        plt.style.use('ggplot') # ['fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
        plt.plot(dates, np.zeros(len(df_with_sentiment['polarity'])), linestyle='-.', linewidth=4, color ='#696969', label='Neutral')
        plt.plot(dates, df_with_sentiment['polarity'], linewidth=3, linestyle='-.', color='blue', label='Polarity slope')
        plt.scatter(dates, df_with_sentiment['polarity'], marker='*', s=200, color='red', label='Data points')
        plt.title("{} - Polarity scores over time (B/w -1 and +1)".format(username), fontsize=40)
        plt.xlabel("Date", fontsize=30)
        plt.ylabel("Polarity score", fontsize=30)
        plt.xticks(fontsize=20, rotation=50)
        plt.yticks(np.arange(-1, 1 + step_size, step=step_size), fontsize=20)
        plt.tight_layout()
        plt.grid()
        plt.legend(loc='best', fontsize=24)
        plt.savefig("{}/{} - Polarity scores over time.png".format(results_path, username))
        
        plt.figure(figsize = (25, 14))
        plt.style.use('ggplot') # ['fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
        plt.plot(dates, df_with_sentiment['subjectivity'], linestyle='-.', linewidth=3, color='blue', label='Subjectivity slope')
        plt.scatter(dates, df_with_sentiment['subjectivity'], marker='*', s=200, color='red', label='Data points')
        plt.title("{} - Subjectivity scores over time (B/w 0 and +1)".format(username), fontsize=40)
        plt.xlabel("Date", fontsize=30)
        plt.ylabel("Subjectivity score", fontsize=30)
        plt.xticks(fontsize=20, rotation=50)
        plt.yticks(np.arange(0, 1 + step_size, step=step_size), fontsize=20)
        plt.tight_layout()
        plt.grid()
        plt.legend(loc='best', fontsize=24)
        plt.savefig("{}/{} - Subjectivity scores over time.png".format(results_path, username))


    def populate_stop_words(self):
        """
        Returns list of stopwords using the 'nltk.corpus' module.
        """
        stop_words = stopwords.words('english')
        return stop_words


    def create_wordcloud(self, df_with_sentiment):
        """
        Creates WordCloud of all words used in the entries.
        """
        comment_words = ' '
        stopwords = self.populate_stop_words()
        
        for entry in df_with_sentiment['tweets']:
            entry = str(entry)
            tokens = entry.split() 
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            
            for words in tokens:
                comment_words = comment_words + words + ' '
        
        # Create object of 'WordCloud'.
        wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=stopwords,
                            min_font_size=10).generate(comment_words)
        
        # Plot.
        plt.figure(figsize = (15, 10), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("{}/{} - WordCloud of original tweets.png".format(results_path, username))




if __name__ == '__main__':

    import warnings
    warnings.filterwarnings("ignore")   
    
    # topic = 'politics'
    # hash_tag_list = ['donald trump', 'hillary clinton', 'barack obama', 'bernie sanders']
    # fetched_tweets_filename = 'tweets_{}.json'.format(topic)
    
    # twitter_client = TwitterClient('pycon')
    # print(twitter_client.get_user_timeline_tweets(2))

    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
    
    results_path = "./results"

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    
    # 'usernames' is a list of Twitter usernames (handles) obtained from another file (check the imports)
    # 'number_of_tweets' is an integer representing the number of tweets to extract via the API
    for username in usernames:
        tweets = api.user_timeline(screen_name=username, count=number_of_tweets)
        
        df = tweet_analyzer.tweets_to_data_frame(tweets)
        df_tweets_original = df[df['tweets'].apply(tweet_analyzer.drop_retweets)]
        df_mentions = tweet_analyzer.get_mention_stats(df)
        
        tweet_analyzer.create_plots(df)
        tweet_analyzer.create_wordcloud(df_tweets_original)

        df.to_csv("{}/{} - Tweet analysis (all).csv".format(results_path, username), index=False)
        df_tweets_original.to_csv("{}/{} - Tweet analysis (originals).csv".format(results_path, username), index=False)
        df_mentions.to_csv("{}/{} - Tweet mentions count.csv".format(results_path, username), index=False)
        
        print("\nUsername: {}\nTweets requested: {}\nTweets extracted: {}\nOriginal tweets: {}".\
            format(username, number_of_tweets, len(df), len(df_tweets_original)))
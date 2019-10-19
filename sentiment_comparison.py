# Twitter, API and NLP related modules
import tweet_analysis
from twitter_handles import usernames, number_of_tweets

# Data manipulation, analysis and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_users_tweets(usernames, number_of_tweets):
    
    df_tweet_info = pd.DataFrame()
    for username in usernames:
        tweets = api.user_timeline(screen_name=username, count=number_of_tweets)

        df = tweet_analyzer.tweets_to_data_frame(tweets)
        df_tweets_original = df[df['tweets'].apply(tweet_analyzer.drop_retweets)]

        sentences = list(df_tweets_original['tweets'])
        corpus = '. '.join(sentences)
        avg_polarity = tweet_analyzer.analyze_polarity(corpus)
        avg_subjectivity = tweet_analyzer.analyze_subjectivity(corpus)
        avg_post_length = round(df_tweets_original['len'].mean(), 2)
        likes_per_post = round(df_tweets_original['likes'].mean(), 2)
        rts_per_post = round(df_tweets_original['retweets'].mean(), 2)
        df_temp = pd.DataFrame({
            'username': username,
            'tweet_corpus': corpus,
            'avg_post_length': avg_post_length,
            'likes_per_post': likes_per_post,
            'rts_per_post': rts_per_post,
            'avg_polarity': avg_polarity,
            'avg_subjectivity': avg_subjectivity
        }, index=[0])
        df_tweet_info = pd.concat([df_tweet_info, df_temp], ignore_index=True, sort=False)
    return df_tweet_info


def plot_likes_rts(df):
    color = 'green'
    plt.style.use('classic') # ['classic', fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
    plt.figure(figsize=(25, 14))
    plt.scatter(x=df['likes_per_post'], y=df['rts_per_post'], s=180, color=color)
    plt.title("Twitter - Likes and Retweets", fontsize=40)
    plt.xlabel("Likes per post", fontsize=30)
    plt.ylabel("RTs per post", fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlim(0, np.ceil(df['likes_per_post'].max()) + 1)
    plt.ylim(0, np.ceil(df['rts_per_post'].max()) + 1)
    for user, fav, rt in zip(df['username'], df['likes_per_post'], df['rts_per_post']):
        plt.text(x=fav, y=rt, s=str(user), fontsize=25, color=color)
    plt.tight_layout()
    plt.grid()
    plt.savefig("{}/Likes and Retweets.png".format(results_path))


def plot_sentiment(df):    
    color = 'red'
    plt.style.use('classic') # ['classic', fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
    plt.figure(figsize=(25, 14))
    plt.scatter(x=df['avg_subjectivity'], y=df['avg_polarity'], s=180, color=color)
    plt.title("Tweet sentiment", fontsize=40)
    plt.xlabel("Average subjectivity", fontsize=30)
    plt.ylabel("Average polarity", fontsize=30)
    plt.xticks(np.arange(0, 1+0.25, 0.25), fontsize=20)
    plt.yticks(np.arange(-1, 1+0.25, 0.25), fontsize=20)
    plt.xlim(0, 1)
    plt.ylim(-1, 1)
    for user, sub, pol in zip(df['username'], df['avg_subjectivity'], df['avg_polarity']):
        plt.text(x=sub, y=pol, s=str(user), fontsize=25, color=color)
    plt.tight_layout()
    plt.grid()
    plt.savefig("{}/Sentiment scores.png".format(results_path))



if __name__ == '__main__':
    twitter_client = tweet_analysis.TwitterClient()
    tweet_analyzer = tweet_analysis.TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    results_path = "./insights_compared"
    ranking_metric = ['likes_per_post', 'rts_per_post', 'avg_polarity', 'avg_subjectivity', 'avg_post_length']
    lower_the_better = [False, False, False, True, True]
    df_info = get_users_tweets(usernames, number_of_tweets)
    df_info.sort_values(by=ranking_metric, ascending=lower_the_better, inplace=True)
    df_info.reset_index(drop=True, inplace=True)
    df_info.to_csv("{}/Tweet comparisons.csv".format(results_path), index=False)
    plot_likes_rts(df_info)
    plot_sentiment(df_info)
    print("Done.")
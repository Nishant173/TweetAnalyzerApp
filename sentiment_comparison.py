# Twitter, API and NLP related modules
import tweet_analysis
from twitter_handles import usernames, number_of_tweets

# Data manipulation, analysis and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_users_tweets(usernames, number_of_tweets):
    """
    Takes in list of 'usernames' and integer of 'number_of_tweets'.
    Returns Pandas DataFrame containing tweet details for those users, and creates CSV file of the same.
    Details include columns labelled:
    ['username', 'tweet_corpus', 'avg_post_length', 'likes_per_post', 'rts_per_post', 'avg_polarity', 'avg_subjectivity']
    """
    df_tweet_info = pd.DataFrame()
    for username in usernames:
        try:
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
            print("Extracted tweets for user: @{}".format(username))
        except Exception as e:
            print("ERROR ({}) - Either username is wrong OR page not found - Handle: @{}".format(e, username))
    
    ranking_metric = ['likes_per_post', 'rts_per_post', 'avg_polarity', 'avg_subjectivity', 'avg_post_length']
    lower_the_better = [False, False, False, True, True]
    df_tweet_info.sort_values(by=ranking_metric, ascending=lower_the_better, inplace=True)
    df_tweet_info.reset_index(drop=True, inplace=True)
    cols = ['username', 'tweet_corpus', 'likes_per_post', 'rts_per_post', 'avg_polarity', 'avg_subjectivity', 'avg_post_length']
    df_tweet_info = df_tweet_info.loc[:, cols]
    df_tweet_info.to_csv("{}/Tweet comparisons (Last {} tweets).csv".format(results_path, number_of_tweets), index=False)
    return df_tweet_info


def plot_likes_rts(df, color='green', tight_layout=False):
    """
    Creates scatter plot for Likes-Retweets comparisons between various users.
    """
    plt.style.use('classic') # ['classic', fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
    plt.figure(figsize=(25, 14))
    plt.scatter(x=df['likes_per_post'], y=df['rts_per_post'], s=180, color=color)
    plt.title("Twitter - Likes and Retweets (Last {} tweets)".format(number_of_tweets), fontsize=40)
    plt.xlabel("Likes per post", fontsize=30)
    plt.ylabel("RTs per post", fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlim(0, np.ceil(df['likes_per_post'].max()) + 1)
    plt.ylim(0, np.ceil(df['rts_per_post'].max()) + 1)
    for user, fav, rt in zip(df['username'], df['likes_per_post'], df['rts_per_post']):
        plt.text(x=fav, y=rt, s=str(user), fontsize=25, color=color)
    if(tight_layout == True):
        plt.tight_layout()
    plt.grid()
    plt.savefig("{}/Likes and Retweets (Last {} tweets).png".format(results_path, number_of_tweets))


def plot_sentiment(df, color='blue', tight_layout=False):
    """
    Creates scatter plot for sentiment comparisons (polarity and subjectivity) between various users.
    """
    plt.style.use('classic') # ['classic', fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
    plt.figure(figsize=(25, 14))
    plt.scatter(x=df['avg_subjectivity'], y=df['avg_polarity'], s=180, color=color)
    plt.title("Tweet sentiment (Last {} tweets)".format(number_of_tweets), fontsize=40)
    plt.xlabel("Average subjectivity", fontsize=30)
    plt.ylabel("Average polarity", fontsize=30)
    plt.xticks(np.arange(0, 1+0.25, 0.25), fontsize=20)
    plt.yticks(np.arange(-1, 1+0.25, 0.25), fontsize=20)
    plt.xlim(0, 1)
    plt.ylim(-1, 1)
    for user, sub, pol in zip(df['username'], df['avg_subjectivity'], df['avg_polarity']):
        plt.text(x=sub, y=pol, s=str(user), fontsize=25, color=color)
    if(tight_layout == True):
        plt.tight_layout()
    plt.grid()
    plt.savefig("{}/Sentiment scores (Last {} tweets).png".format(results_path, number_of_tweets))


def plot_tweet_length(df, color='#1DC34E', tight_layout=False):
    """
    Creates horizontal bar chart for average character count per post, between various users.
    """
    df.sort_values(by='avg_post_length', ascending=True, inplace=True)

    plt.style.use('classic') # ['classic', fivethirtyeight', 'seaborn-dark', 'seaborn-ticks', 'ggplot']
    plt.figure(figsize=(25, 14))
    plt.barh(y=df['username'], width=df['avg_post_length'], color=color)
    plt.title("Tweet length (Last {} tweets)".format(number_of_tweets), fontsize=40)
    plt.xlabel("Average tweet length (characters)", fontsize=30)
    plt.ylabel("Usernames", fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlim(0, np.ceil(df['avg_post_length'].max()) + 10)
    for user, length in zip(df['username'], df['avg_post_length']):
        plt.text(x=length + 0.2, y=user, s=str(length), fontsize=25, color=color)
    if(tight_layout == True):
        plt.tight_layout()
    plt.grid()
    plt.savefig("{}/Tweet length (Last {} tweets).png".format(results_path, number_of_tweets))



if __name__ == '__main__':
    twitter_client = tweet_analysis.TwitterClient()
    tweet_analyzer = tweet_analysis.TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    results_path = "./insights_compared"
    df_info = get_users_tweets(usernames, number_of_tweets)
    plot_likes_rts(df=df_info, color='purple', tight_layout=False)
    plot_sentiment(df=df_info, color='green', tight_layout=False)
    plot_tweet_length(df=df_info, color='#1DC34E', tight_layout=False)
    print("Done.")
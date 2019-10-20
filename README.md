# TweetAnalyzerApp
- Uses [Twitter API](https://developer.twitter.com) to extract tweets from user-handles.
- Tweets are then analyzed.
- Insights such as sentiment of tweets, mention frequencies, wordclouds and more are extracted.
- On running `tweet_analysis.py`, Three CSV files and three PNG files are created (per username) and stored in the `results` folder.
- Insights such as comparisons of likes, retwets, and sentiment of tweets are extracted.
- On running `sentiment_comparison.py`, one CSV file and two PNG files are created and stored in the `insights_compared` folder.

## Usage
- Add credentials into the `twitter_credentials.py` file.
- Create two folder names `results` and `insights_compared` to store insights from `tweet_analysis.py` and `sentiment_comparison.py` respectively.
- Run `tweet_analysis.py` after updating the `usernames` list found in the import on line #8.
- Run `sentiment_comparison.py` after updating the `usernames` list found in the import on line #3.

## Dependencies
Do `pip install -r requirements.txt`
- tweepy==3.6.0
- json==2.0.9
- numpy==1.15.4
- pandas==0.25.1
- matplotlib==2.2.2
- re==2.2.1
- textblob==0.15.1
- wordcloud==1.5.0
- nltk==3.4.5

# TweetAnalyzerApp
- Uses [Twitter API](https://developer.twitter.com) to extract tweets from user-handles.
- Tweets are then analyzed.
- Insights such as sentiment of tweets, mention frequencies, wordclouds and more are extracted.
- Three CSV files and three PNG files are created and stored in the `results` folder.

## Usage
- Add credentials into the `twitter_credentials.py` file.
- Run `main.py` after updating the `usernames` list on line #313, as per your preference.

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

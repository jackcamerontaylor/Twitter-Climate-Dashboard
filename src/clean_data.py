import pandas as pd
import re
from textblob import TextBlob

from .models import hugging_face_tweet_sentiment

def clean_text(text):
    """
    Cleans necessary text from the tweet, preparing it for sentiment analysis.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove user @ references and '#'
    text = re.sub(r'\@\w+|\#','', text)
    # Remove special characters, numbers, punctuations (except for apostrophes)
    text = re.sub(r"[^a-zA-Z' ]+", '', text)
    return text

def analyse_sentiment(tweet):
    """
    Huggingface transformers based sentiment analyser. This gives a positive
    and negative score. It is pretrained to deal specifically with tweets.
    """
    analysis = hugging_face_tweet_sentiment(tweet)

    return analysis[0]

def clean_tweets(tweets: list) -> pd.DataFrame:
    """
    This will take the output from the collect_tweets model and clean it.
    """
    df = pd.DataFrame(tweets, columns=[
        'Tweet ID',               # Used to drop the same tweets
        'User ID',                # Unique identifier of the user
        'Location',               # User's location
        'Sensitive',              # Indicates if the users content is sensitive
        'Followers',              # Number of followers
        'Following',              # Number of accounts the user follows
        'Number of Tweets',       # Number of tweets posted by the user
        'Created',                # Date and time the tweet was created
        'Tweet Text',             # The text content of the tweet
        'Favorite Count',         # Number of favourites on the tweet
        'Retweet Count'           # Number of retweets
    ])

    df['Clean Tweet Text'] = df['Tweet Text'].apply(clean_text)

    df['Sentiment'] = df['Clean Tweet Text'].apply(analyse_sentiment)

    df['Location'] = df['Location'].fillna('Unknown')

    return df

def update_tweets(clean_tweets: pd.DataFrame):
    """
    This will merge the clean tweets with the already clean ones in the csv.
    """
    tweets = pd.read_csv("tweets_store/tweets.csv")

    concat = pd.concat([tweets, clean_tweets], ignore_index=True)

    concat.drop(['Unnamed: 0', 'Clean Tweet Text'], axis=1, inplace=True)

    concat.drop_duplicates('Tweet Text', inplace=True)

    concat.to_csv("tweets_store/tweets.csv")

def clean_data(tweets: list):
    """
    Main function for this file.
    """
    cleaned_tweets = clean_tweets(tweets)
    update_tweets(cleaned_tweets)
from twikit import Client
import pandas as pd
from src.config import USERNAME, EMAIL, PASSWORD
# Initialize client
client = Client('en-UK')

client.login(
    auth_info_1=USERNAME ,
    auth_info_2=EMAIL,
    password=PASSWORD
)

# Initialize an empty list to store tweet data
tweets_data = []
while 2>1:
    # Search for tweets
    tweets = client.search_tweet('ClimateChange OR GlobalWarming OR Sustainability', 'Latest')

    # Iterate over the tweets and store relevant data in the list
    for tweet in tweets:
        tweets_data.append([tweet.user.name, tweet.created_at, tweet.text, tweet.user.location, tweet.favorite_count, tweet.retweet_count])

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(tweets_data, columns=['User', 'Date', 'Tweet', 'Location', 'Likes', 'Retweets'])

    # Save the DataFrame to a CSV file
    df.to_csv('climate_change_tweets.csv', index=False)

    print("Data collection complete. Tweets saved to climate_change_tweets.csv")
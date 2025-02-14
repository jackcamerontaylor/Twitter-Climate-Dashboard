from twikit import Client
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .config import USERNAME, EMAIL, PASSWORD

# Initialise client
client = Client('en-UK')

async def main() -> list[list]:
    """
    Login for the client and recieves the last 20 tweets with the specified key words.

    The search_tweet function gets the most recent 20 tweets, maybe we create a large
    csv and just run the update funciton every once in a while which should keep the
    dashboard updated? If so, we should append after the tweets are cleaned, which 
    can be done in the clean_data file.
    """
    await client.login(
        auth_info_1=USERNAME ,
        auth_info_2=EMAIL,
        password=PASSWORD
    )

    today = date.today()
    last_month = today - relativedelta(month=1)
    tweets = await client.search_tweet(f'"climate change" AND "Scotland" since:{last_month.strftime("%Y-%m-%d")} until:{today.strftime("%Y-%m-%d")}', 'Top')

    tweets_data = []
    for tweet in tweets:
        # need to append as much MEANINGFUL information as possible
        # FIXME: Can add more from here https://twikit.readthedocs.io/en/latest/twikit.html#twikit.client.client.Client.search_tweet
        tweets_data.append([tweet.id,
                            tweet.user.id, # this should be the unique identifier of the user
                            tweet.user.location,
                            tweet.user.possibly_sensitive, # are they snowflakes?...
                            tweet.user.followers_count,
                            tweet.user.following_count,
                            tweet.user.statuses_count, # number of tweets the user posted
                            tweet.created_at, 
                            tweet.text, 
                            tweet.favorite_count, 
                            tweet.retweet_count])
        
    return tweets_data
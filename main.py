import asyncio

from src.collect_tweets import main
from src.clean_data import clean_data

if __name__ == "__main__":
    tweets = asyncio.run(main())
    clean_data(tweets)

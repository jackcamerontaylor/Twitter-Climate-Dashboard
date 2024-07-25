import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from twikit import Client
from .config import USERNAME, EMAIL, PASSWORD
import asyncio

# Can change the port to defualt which is 50, but I have been running it on 54. It can be accessed by running
# python dashboard.py in the terminal and then searching http://127.0.0.1:8054/ in you preferred browser

# Initialize client
client = Client('en-UK')

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Twitter Dashboard"

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.H1("Twitter Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.H2("In this dashboard, you can view and analyze tweets about whatever topic you want.", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div([
            html.H3("What topic would you like to search for? Split each topic by a comma:", style={'color': '#34495e'}),
            dcc.Input(id='search-input', type='text', style={'width': '50%'}),
        ], style={'margin': '20px 0'}),

        html.Div([
            html.H3("How many tweets would you like to collect? (1-200):", style={'color': '#34495e'}),
            dcc.Input(id='count-input', type='number', min=1, max=200, style={'width': '20%'}),
        ], style={'margin': '20px 0'}),

        html.Div([
            html.H3("Select the search option:", style={'color': '#34495e'}),
            dcc.Dropdown(
                id='search-option',
                options=[
                    {'label': 'Top', 'value': 'Top'},
                    {'label': 'Latest', 'value': 'Latest'},
                    {'label': 'Media', 'value': 'Media'}
                ], style={'width': '50%'}
            ),
        ], style={'margin': '20px 0'}),

        html.Button('Collect data', id='collect-button', n_clicks=0, style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'cursor': 'pointer'}),

        html.Div(id='tweet-data-output', style={'marginTop': '20px'}),
        
        html.H2("Top 3 Most Liked Tweets", style={'color': '#2c3e50', 'marginTop': '40px'}),
        html.Div(id='top-liked-tweets', style={'marginTop': '20px'}),
        
        html.H2("Top 3 Most Retweeted Tweets", style={'color': '#2c3e50', 'marginTop': '40px'}),
        html.Div(id='top-retweeted-tweets', style={'marginTop': '20px'}),
    ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
    
    html.Div([
        html.H2("Input Text for Sentiment Analysis", style={'color': '#2c3e50', 'marginTop': '40px'}),
        dcc.Input(id='input-text', type='text', style={'width': '50%'}),
        html.Button('Analyze', id='analyze-button', n_clicks=0, style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'cursor': 'pointer'}),
        html.Div(id='sentiment-output', style={'marginTop': '20px'}),
        dcc.Graph(id='sentiment-bar-chart', style={'marginTop': '40px'}),
    ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'marginTop': '40px'})
], style={'backgroundColor': '#f0f0f5', 'padding': '20px 0'})

# Create a global variable to store the DataFrame
global_df = pd.DataFrame()

async def fetch_tweets(topics, search_option, count_input):
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    # Search for tweets
    tweets = await client.search_tweet(topics, search_option, count=count_input)
    return tweets

@app.callback(
    [Output('tweet-data-output', 'children'),
     Output('top-liked-tweets', 'children'),
     Output('top-retweeted-tweets', 'children')],
    [Input('collect-button', 'n_clicks')],
    [State('search-input', 'value'),
     State('count-input', 'value'),
     State('search-option', 'value')]
)
def update_tweets(n_clicks, search_input, count_input, search_option):
    global global_df

    if n_clicks > 0:
        if not search_input or not count_input or not search_option:
            return ("Please provide search topics, number of tweets, and search option.", "", "")

        if count_input < 1 or count_input > 200:
            return ("Please enter a number of tweets between 1 and 200.", "", "")

        # Reset the tweets_data list
        tweets_data = []

        # Split the search input by comma and join with OR
        topics = ' OR '.join(search_input.split(','))

        # Fetch tweets
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tweets = loop.run_until_complete(fetch_tweets(topics, search_option, count_input))

        # Iterate over the tweets and store relevant data in the list
        for tweet in tweets:
            tweets_data.append([tweet.user.name, tweet.created_at, tweet.text, tweet.user.location, tweet.favorite_count, tweet.retweet_count])

        # Convert the list to a pandas DataFrame
        global_df = pd.DataFrame(tweets_data, columns=['User', 'Date', 'Tweet', 'Location', 'Likes', 'Retweets'])

        # Find the top liked and retweeted tweets
        top_liked_tweets = global_df.nlargest(3, 'Likes')
        top_retweeted_tweets = global_df.nlargest(3, 'Retweets')

        liked_list = html.Ul([html.Li(f"{tweet['User']} (Likes: {tweet['Likes']}): {tweet['Tweet']}") for _, tweet in top_liked_tweets.iterrows()])
        retweeted_list = html.Ul([html.Li(f"{tweet['User']} (Retweets: {tweet['Retweets']}): {tweet['Tweet']}") for _, tweet in top_retweeted_tweets.iterrows()])

        return "", liked_list, retweeted_list

    return "", "", ""

if __name__ == '__main__':
    app.run_server(debug=True, port=8054)

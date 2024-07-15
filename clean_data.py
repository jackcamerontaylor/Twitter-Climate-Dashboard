import pandas as pd
import re
from textblob import TextBlob

df = pd.read_csv('climate_change_tweets.csv')

# Handle Missing Values
# Fill missing values in 'Location' with 'Unknown'
df['Location'] = df['Location'].fillna('Unknown')

# Remove Duplicates
df = df.drop_duplicates()

# Clean Text Data
def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove user @ references and '#'
    text = re.sub(r'\@\w+|\#','', text)
    # Remove special characters, numbers, punctuations (except for apostrophes)
    text = re.sub(r"[^a-zA-Z' ]+", '', text)
    return text

df['Tweet'] = df['Tweet'].apply(clean_text)

# Remove Duplicates based on 'Tweet' column
df = df.drop_duplicates(subset='Tweet')

# Perform Sentiment Analysis
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    return analysis.sentiment.polarity

df['Sentiment'] = df['Tweet'].apply(analyze_sentiment)

# Bin Sentiment Scores
df['SentimentBin'] = pd.cut(df['Sentiment'], bins=[0, 0.2, 0.4, 0.6, 0.8, 1], labels=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'])

# Save the cleaned DataFrame with Sentiment to a new CSV file
df.to_csv('cleaned_climate_change_tweets_with_sentiment.csv', index=False)


import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px

cleaned_df = pd.read_csv('cleaned_climate_change_tweets_with_sentiment.csv')


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Twitter Sentiment Analysis Dashboard"),
    dcc.Dropdown(
        id='sentiment-dropdown',
        options=[
            {'label': 'Positive', 'value': 'Positive'},
            {'label': 'Negative', 'value': 'Negative'}
        ]
    ),
    html.H2(id='top-tweets-title'),
    html.Div(id='tweets-display'),
    html.H2("Top 3 Most Liked Tweets"),
    html.Div(id='top-liked-tweets'),
    html.H2("Top 3 Most Retweeted Tweets"),
    html.Div(id='top-retweeted-tweets'),
    dcc.Graph(id='sentiment-bar-chart'),
    html.H2("Input Text for Sentiment Analysis"),
    dcc.Input(id='input-text', type='text', style={'width': '50%'}),
    html.Button('Analyze', id='analyze-button', n_clicks=0),
    html.Div(id='sentiment-output')
])

# Callback to update the tweet display based on selected sentiment
@app.callback(
    [Output('top-tweets-title', 'children'),
     Output('tweets-display', 'children')],
    [Input('sentiment-dropdown', 'value')]
)
def update_tweets(selected_sentiment):
    title = "Please select a sentiment to display the top 5 tweets."
    top_5_tweets = cleaned_df[0:5]

    if selected_sentiment == 'Positive':
        title = "Top 5 Most Positive Tweets"
        top_5_tweets = cleaned_df.nlargest(5, 'Sentiment')
    elif selected_sentiment == 'Negative':
        title = "Top 5 Most Negative Tweets"
        top_5_tweets = cleaned_df.nsmallest(5, 'Sentiment')

    tweet_list = html.Ul([html.Li(f"{tweet['User']} (Likes: {tweet['Likes']}, Retweets: {tweet['Retweets']}): {tweet['Tweet']}") for _, tweet in top_5_tweets.iterrows()])
    return title, tweet_list

# Callback to update the most liked and retweeted tweets
@app.callback(
    [Output('top-liked-tweets', 'children'),
     Output('top-retweeted-tweets', 'children')],
    [Input('sentiment-dropdown', 'value')]
)
def update_top_tweets(selected_sentiment):

    top_liked_tweets = cleaned_df.nlargest(3, 'Likes')
    top_retweeted_tweets = cleaned_df.nlargest(3, 'Retweets')

    liked_list = html.Ul([html.Li(f"{tweet['User']} (Likes: {tweet['Likes']}): {tweet['Tweet']}") for _, tweet in top_liked_tweets.iterrows()])
    retweeted_list = html.Ul([html.Li(f"{tweet['User']} (Retweets: {tweet['Retweets']}): {tweet['Tweet']}") for _, tweet in top_retweeted_tweets.iterrows()])

    return liked_list, retweeted_list

# Callback to update the sentiment bar chart
@app.callback(
    Output('sentiment-bar-chart', 'figure'),
    [Input('sentiment-dropdown', 'value')]
)
def update_bar_chart(selected_sentiment):
    sentiment_counts = df['SentimentBin'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    fig = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Distribution')
    fig.update_layout(xaxis_title='Sentiment Category', yaxis_title='Count')
    return fig

# Callback to perform sentiment analysis on user input text
@app.callback(
    Output('sentiment-output', 'children'),
    [Input('analyze-button', 'n_clicks')],
    [dash.dependencies.State('input-text', 'value')]
)
def analyze_input_text(n_clicks, input_text):
    if n_clicks > 0 and input_text:
        sentiment_score = analyze_sentiment(input_text)
        return f"Sentiment Score: {sentiment_score}"
    return ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
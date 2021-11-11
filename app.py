from flask import Flask, render_template, request
import pandas as pd
import json
import plotly.graph_objs as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly
import numpy as np
from wordcloud.wordcloud import WordCloud 

accessToken = "216111107-PuNWn73xXIm2I8KNyLjnqp0yeuL2huNOuYJqsPOp"
accessTokenSecret = "UR0blltttJ4ZMrBPkoCAvTZThn9bZ1AYdCeen0WFtKOnK"
apiKey = "0WyEYyOyQZNfZnuyPDaEryKYF"
secretKey = "OrMJYIVgXwsjRHs8RuYPX6hLkvDkjNg8tLaTVDhwZ2knVwugZd"

from TwitterAPI import TwitterAPI
api = TwitterAPI(apiKey, secretKey, accessToken, accessTokenSecret)

############## Rendering landing page ####################

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('landingPage.html')

@app.route('/about')
def about():
    return render_template('about.html')    

############## Creating user input feature and assigning the input to the text variable which will be used throughout the script ####################
############## Creating API calls to Twitter API ############## 

@app.route('/', methods=['POST'])
def my_form_post():

   text = request.form['text']
   text = ('"' + text + '"')   

   bar = barPlot()  
   line = linePlot()
   compoundScore = compoundScoreCard()
   sentiment = vadarSentimentAnalysis()
   data = linePlot()
   tweets = latestTweetsDataFrame()
   text = text

   return render_template('dashboard.html', bar=bar, sentiment=sentiment, tables=[tweets.to_html(classes='data')], line=line, scorecard=compoundScore, data=data, text=text)

def tweetAPICall():

   text = request.form['text']
   text = ('"' + text + '"') 

   query1 = api.request('search/tweets', {'q': text, 
                                  'count': 100,
                                  'lang': 'en',
                                  'until': '2021-10-31'})

   query2 = api.request('search/tweets', {'q': text, 
                                  'count': 100,
                                  'lang': 'en',
                                  'until': '2021-10-30'}) 

   query3 = api.request('search/tweets', {'q': text, 
                                  'count': 100,
                                  'lang': 'en',
                                  'until': '2021-10-29'})                                

   tweetResponse=[]
   tweetDate=[]
   tweetLocation=[]

   #### For loop to iterate through JSON response from server and append required values into lists   
   for x in query1: 
        tweetResponse.append(x['text'])
        tweetDate.append(x['created_at'])
        tweetLocation.append(x['user']['location'])


   for x in query2: 
        tweetResponse.append(x['text'])
        tweetDate.append(x['created_at'])  
        tweetLocation.append(x['user']['location'])


   for x in query3: 
        tweetResponse.append(x['text'])
        tweetDate.append(x['created_at'])  
        tweetLocation.append(x['user']['location']) 
     
        twitterData = pd.DataFrame({'Tweets': tweetResponse,
                              'Tweet Date': tweetDate,
                              'Tweet Location': tweetLocation})    

        
        return twitterData

######### Vadar Sentiment Analysis function, passing the tweetAPICall variable for use within this function         

def vadarSentimentAnalysis():

     analyzer = SentimentIntensityAnalyzer()
     positiveSentiment = []
     negativeSentiment = [] 
     neutralSentiment = []
     compoundSentiment = []

     twitterData = tweetAPICall()
     date = twitterData['Tweet Date']

     for tweet in twitterData['Tweets']:
        vs = analyzer.polarity_scores(tweet)
        positiveSentiment.append(vs['pos'])
        negativeSentiment.append(vs['neg'])
        neutralSentiment.append(vs['neu'])
        compoundSentiment.append(vs['compound'])
        
     sentimentData = {'Tweet Date': date,
                'Positive Sentiment': positiveSentiment,
                'Negative Sentiment': negativeSentiment,
                'Neutral Sentiment': neutralSentiment,
                'Compound Sentiment': compoundSentiment}

     sentimentDataFrame = pd.DataFrame(sentimentData)

     

     return sentimentDataFrame

def barPlot():

        sentimentDataFrame = vadarSentimentAnalysis()  

        positiveTweets = []
        negativeTweets = []

        for value in sentimentDataFrame['Compound Sentiment']:
             if value >= 0:
                  positiveTweets.append(value)
             else:
                  negativeTweets.append(value)     

        barFig = go.Figure([go.Bar( 
        x=['Positive Sentiment'],
        y=[len(positiveTweets)],
        name="Positive Tweets")])

        barFig.add_trace(
             go.Bar(
                  x=['Negative Sentiment'],
                  y=[len(negativeTweets)],
                  name="Negative Tweets"))

        barFig.update_layout(     
        autosize=False,
        width=375,
        height=175,
        margin=dict(
        l=5,
        r=5,
        b=5,
        t=5),
        paper_bgcolor="#27293d",
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
        font=dict(
             color="white"
        ))

        barFig.update_xaxes(title_text='Tweet Sentiment')
        barFig.update_yaxes(title_text='Total Tweets')
        barFig.update_layout(showlegend=False)
        barFig.update_traces(marker_color='#e14eca')

        barGraphJSON = json.dumps(barFig, cls=plotly.utils.PlotlyJSONEncoder)

        return barGraphJSON


def linePlot():

     tweetData = vadarSentimentAnalysis()
     tweetData['Tweet Date'] = pd.to_datetime(tweetData['Tweet Date']).dt.strftime('%d-%m-%Y')

     dateOne = tweetData.loc[tweetData['Tweet Date'] == '28-10-2021']
     dateTwo = tweetData.loc[tweetData['Tweet Date'] == '29-10-2021']
     dateThree = tweetData.loc[tweetData['Tweet Date'] == '30-10-2021']

     meanOne = dateOne['Compound Sentiment'].mean()
     meanTwo = dateTwo['Compound Sentiment'].mean()
     meanThree = dateThree['Compound Sentiment'].mean()

     lineFig = go.Figure(data=go.Scatter(x=['31/10/2021', '01/11/2021', '02/11/2021'], 
     y=[meanOne, meanTwo, meanThree]))

     lineFig.update_layout(
        autosize=False,
        width=825,
        height=200, 
        margin=dict(
        l=5,
        r=5,
        b=5,
        t=5),
        paper_bgcolor="#27293d",
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
        font=dict(
             color="white"
        ))
        
     lineFig.update_xaxes(title_text='Tweet Date')
     lineFig.update_yaxes(title_text='Compound Daily Sentiment Score')
     lineFig.update_traces(marker_color='#e14eca')

     lineGraphJSON = json.dumps(lineFig, cls=plotly.utils.PlotlyJSONEncoder)

     return lineGraphJSON

def compoundScoreCard():

        sentimentData = vadarSentimentAnalysis()  

        netCompoundScore= np.mean(sentimentData['Compound Sentiment'])
        roundedNetCompoundScore = float("{:.2f}".format(netCompoundScore))
        
        return roundedNetCompoundScore

def latestTweetsDataFrame():

     tweets = tweetAPICall()

     latestTweets = tweets['Tweets']
     location = tweets['Tweet Location']

     tweetDF = pd.DataFrame({'Tweets': latestTweets, 'Location': location}) 

     return tweetDF

app.run(debug=True, use_debugger=False, use_reloader=False)









#Importing Libraries
from flask import Flask,render_template,request,url_for,redirect,session,jsonify
from sklearn.externals import joblib
import re
import tweepy
from tweepy import OAuthHandler

#Creating Flask App
app=Flask(__name__)

#Loading Models from Directory
new_model = joblib.load('mlmodel.pkl')
new_token = joblib.load('tfidf.pkl')

consumer_key = "QNQZHNNo6RivPNd2pqPxCQajt"
consumer_secret = "kaxsk0dJsWWw05uxKwDtK5WMT9PblTIEzYwFF9bPL8TSkhRpI1"
access_token = "710828734228471808-bBWduho6oNWzvjtvtm1YlKkcFxmwLgD"
access_token_secret = "enkBS23PiSMI9cl5HSxh7Ovf8GrJlYdwdRL23TcdLGuE2"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


#Redirecting to index.html
@app.route("/" , methods  = ['POST','GET'])

#Fetching input
def index():
	answer = '' #Output field
	if request.method == 'POST':
		if request.form['tquery'] == "":
			text  = request.form['text']
			tokenized = new_token.transform([text])
			predictions = new_model.predict(tokenized) #Predicting the sentiment

			res = predictions[0]

			if res==1:
				answer = 'Positive'
			else:
				answer = 'Negative'

		


		elif request.form['text'] == "":
			query_enter = request.form['tquery']

			tweets = []

			fetched_tweets = api.search(q = query_enter, lang='en', count = 25)

			for tweet in fetched_tweets:
				parsed_tweet = tweet.text

				if tweet.retweet_count > 0:
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)

				else:
					tweets.append(parsed_tweet)

			length = len(tweets)
			cleaned_tweets = []

			for i in range(0, length):
				cleaned_text =  ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(https?://[A-Za-z0-9./]+)", " ", tweets[i]).split())
				cleaned_tweets.append(cleaned_text)

			results = []
			ptweets = 0
			ntweets = 0
			answer = ''

			for i in range(0, length):
				tokenized = new_token.transform([cleaned_tweets[i]])
				predictions = new_model.predict(tokenized)

				res = predictions[0]

				if res==1:
					ptweets = ptweets+1

				else:
					ntweets = ntweets+1

				results.append(res)

			ppercentage = round(((ptweets/length)*100),2)
			npercentage = 100-ppercentage

			if (ptweets>ntweets):
				answer = query_enter + " - "+str(ppercentage)+'% Positive out of '+str(length)+' tweets'

			elif (ntweets>ptweets):

				answer = query_enter + " - "+str(npercentage)+'% Negative out of '+str(length)+' tweets'

			else:
				answer = query_enter+' Neutral'

	#Returning output to index.html
	return render_template('index.html',answer = answer)

if __name__=="__main__":
	app.run(port=5000,debug=True)
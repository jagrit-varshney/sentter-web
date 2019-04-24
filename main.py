#Importing Libraries
from flask import Flask,render_template,request,url_for,redirect,session,jsonify
from sklearn.externals import joblib
import tweepy
from tweepy import OAuthHandler

#Creating Flask App
app=Flask(__name__)

#Loading Models from Directory
new_model = joblib.load('mlmodel.pkl')
new_token = joblib.load('tfidf.pkl')

consumer_key = "XXXX"
consumer_secret = "XXXX"
access_token = "XXXX"
access_token_secret = "XXXX"
# Enter your API keys in the above four variables.

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

			fetched_tweets = api.search(q = query_enter, lang='en', count = 100)

			for tweet in fetched_tweets:
				parsed_tweet = tweet.text

				if tweet.retweet_count > 0:
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)

				else:
					tweets.append(parsed_tweet)

			length = len(tweets)
			results = []
			ptweets = 0
			ntweets = 0
			answer = ''

			for i in range(0, length):
				tokenized = new_token.transform([tweets[i]])
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

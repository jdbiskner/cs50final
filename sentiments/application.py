from flask import Flask, redirect, render_template, request, url_for

import helpers
import os
import sys
from analyzer import Analyzer

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():

    # validate screen_name
    screen_name = request.args.get("screen_name", "")
    if not screen_name:
        return redirect(url_for("index"))

    if helpers.get_user_timeline(screen_name) == None:
        return redirect(url_for("index"))
    
    # get screen_name's tweets
    tweets = helpers.get_user_timeline(screen_name)

    # TODO
    positive, negative, neutral = 0.0, 0.0, 0.0
    positives = os.path.join(sys.path[0], "positive-words.txt")
    negatives = os.path.join(sys.path[0], "negative-words.txt")
    analyzer = Analyzer(positives, negatives)
    
    # iterate through tweets to get score
    for tweet in tweets:

        # grab tweetscore from analyze        
        tweetscore = analyzer.analyze(tweet)
        
        # add tweet to positive, negative, or neutral scores
        if tweetscore > 0.0:
            positive += 1
        elif tweetscore < 0.0:
            negative += 1
        else:
            neutral += 1

    # recalculate the percentages
    tweetSum = positive + negative + neutral
    positive = (positive / tweetSum) * 100
    negative = (negative / tweetSum) * 100
    neutral = (neutral / tweetSum) * 100

    # generate chart
    chart = helpers.chart(positive, negative, neutral)

    # render results
    return render_template("search.html", chart=chart, screen_name=screen_name)

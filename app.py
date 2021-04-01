from flask import Flask, render_template, request
from twitterscraper import query_tweets
from flask_mysqldb import MySQL

import asyncio
import datetime as dt
import pandas as pd

app = Flask(__name__)
mysql = MySQL(app)
cur = mysql.connection.cursor()

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "web_tech_final_project"
# app.config['MYSQL_PORT'] = 3645    # this can change based on the system or dockerfile used


async def getQuery(phrase):

    # begining date to search for
    begin_date = dt.date(2019, 4, 15)
    # end date
    end_date = dt.date(2020, 3, 14)
    # upper limit for total tweets scrapped
    limit = 100
    # language to use
    lang = 'english'

    tweets = query_tweets(phrase, begindate=begin_date,
                          enddate=end_date, limit=limit, lang=lang)

    df = pd.DataFrame(t.__dict__ for t in tweets)

    print("Twitter Scrap Successful!")

    # intialiing variables that will be collected from scrapper
    t_username = ""
    t_tweet = ""
    t_location = ""

    for i, j in df.iterrows():
        if i == 'screen_name':
            t_username = j
        if i == 'text':
            t_tweet = j
    # this is not always guaranteed as this will only
    # have a value if the user added their location to the tweet
        if i == 'location':
            t_location = j
    # at this stage of looping through the current object(tweet information), all the required
    # information is assigned to a execute query to add current tweet to the database
        cur.execute("INSERT INTO tweets (username, tweet, location) VALUES (%s, %s, %s)",
                    (t_username, t_tweet, t_location))
    # nullify the variables for the next tweet object
        t_username = ""
        t_tweet = ""
        t_location = ""

    # commit the changes to the database
    mysql.connection.commit()
    # return from event loop
    return

# creating the event loop to run the twitter scraper
loop = asyncio.get_event_loop()


@app.route('/', methods=['POST', 'GET'])
def index():

    data = "Feedback: here is where the scraped tweets will be displayed!"

    if request.method == 'POST':
        phrase = request.form['phrase']

        # wainting for the webscrapper to finish
        loop.run_until_complete(getQuery(phrase))

        retrived_tweets = cur.execute("SELECT * FROM tweets")
        if retrived_tweets > 0:
            tweetsDetails = cur.fetchall()

        # Removed all records just to have a clean table each request for testing, but this can be
        # commented out to keep the data persistent
        cur.execute("DELETE FROM tweets")
        mysql.connection.commit()

        cur.close()

        data = "Feedback: Tweets scraped successful with phrase '%s'" % phrase

        return render_template('index.html', data=data, tweetsDetails=tweetsDetails)

    elif request.method == 'GET':
        data = "Feedback: here is where the scraped tweets will be displayed!"

        return render_template('index.html', data=data)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)

from flask import Flask, redirect, render_template, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import Tweet, Character, Hashtag, Mention, connect_db, db
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shhsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///sesametweet')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
connect_db(app)

num_tweets_to_display = 10
minutes_to_update = 15


def check_for_updates():
    characters = Character.query.all()
    for character in characters:
        character.update()


sched = BackgroundScheduler(daemon=True)
sched.add_job(check_for_updates, 'interval', minutes=minutes_to_update)
sched.start()

if __name__ == "__main__":
    app.run()


@app.route('/')
def show_all_tweets():
    tweets = Tweet.query.order_by(
        Tweet.date.desc()).limit(num_tweets_to_display)
    return render_template('tweets.html', tweets=tweets)


@app.route('/tweets/page/<int:page_number>')
def get_next_page_tweets(page_number):
    offset_query = page_number * num_tweets_to_display

    tweets = [tweet.serialize() for tweet in Tweet.query.order_by(Tweet.date.desc()).offset(
        offset_query).limit(num_tweets_to_display + 1)]

    if len(tweets) == num_tweets_to_display + 1:
        return jsonify(tweets=tweets[:num_tweets_to_display], page=page_number + 1, end=False)
    else:
        return jsonify(tweets=tweets, page=page_number + 1, end=True)


@app.route('/characters')
def show_characters():
    characters = Character.query.order_by(Character.name).all()
    return render_template('characters.html', characters=characters)


@app.route('/characters/<int:character_id>')
def show_profile_page(character_id):
    character = Character.query.get_or_404(character_id)
    tweets = Tweet.query.filter_by(
        character_id=character_id).order_by(Tweet.date.desc()).limit(num_tweets_to_display)
    return render_template('character_profile.html', character=character, tweets=tweets)


@app.route('/characters/<int:character_id>/page/<int:page_number>')
def get_next_page_character(character_id, page_number):
    offset_query = page_number * num_tweets_to_display
    tweets = [tweet.serialize() for tweet in Tweet.query.filter_by(
        character_id=character_id).order_by(Tweet.date.desc()).offset(offset_query).limit(num_tweets_to_display + 1)]

    if len(tweets) == num_tweets_to_display + 1:
        return jsonify(tweets=tweets[:num_tweets_to_display], page=page_number + 1, end=False)
    else:
        return jsonify(tweets=tweets, page=page_number + 1, end=True)


@app.route('/hashtags/<string:hashtag_text>')
def show_hashtag_tweets(hashtag_text):
    hashtag = Hashtag.query.get_or_404(hashtag_text)
    return render_template('hashtag.html', hashtag=hashtag)


@app.route('/hashtags')
def show_hashtags():
    hashtags = Hashtag.query.order_by(Hashtag.text).all()
    return render_template('hashtags.html', hashtags=hashtags)


@app.route('/mentions/<string:screen_name>')
def show_mention_tweets(screen_name):
    mention = Mention.query.get_or_404(screen_name)
    return render_template('mention.html', mention=mention)


@app.route('/mentions')
def show_mentions():
    mentions = Mention.query.order_by(Mention.followers_count.desc()).all()
    return render_template('mentions.html', mentions=mentions)

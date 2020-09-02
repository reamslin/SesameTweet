from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Tweet, Character, User, Author, connect_db, db
import requests
import twitter
from forms import RegisterForm, TweetForm, LoginForm
from secrets import *
app = Flask(__name__)
app.config['SECRET_KEY'] = "new kesef!"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sesametweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
connect_db(app)

api = twitter.Api(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token_key=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    cache=None,
    tweet_mode='extended')


@app.route('/')
def show_all_tweets():

    if 'user_id' in session:
        current_user = User.query.get_or_404(session['user_id'])
        sesame_characters = Character.query.all()
        tweets = []
        for character in sesame_characters:
            tweets.extend(character.author.tweets)

        tweets.extend(current_user.author.tweets)

        tweets.sort(key=lambda t: t.date, reverse=True)
        return render_template('all_tweets.html', tweets=tweets)
    else:
        return redirect('/register')


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def handle_register():
    if 'user_id' in session:
        return redirect('/')
    else:
        form = RegisterForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            name = form.name.data

            new_user = User.register(
                username=username, password=password, name=name)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return redirect('/')
        else:
            return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username, password=password)
        if user:
            session['user_id'] = user.id
            return redirect('/')
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template("login.html", form=form)


@app.route('/users/<int:user_id>/tweets/new', methods=['GET', 'POST'])
def new_tweet(user_id):
    if 'user_id' in session:

        current_user = User.query.get_or_404(session['user_id'])
        form = TweetForm()

        if form.validate_on_submit():
            text = form.text.data

            new_tweet = Tweet(text=text,
                              author_id=current_user.author_id)
            db.session.add(new_tweet)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('new_tweet.html', form=form)

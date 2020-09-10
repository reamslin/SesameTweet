from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Tweet, Character, User, Author, Hashtag, Mention, connect_db, db
import requests
from forms import RegisterForm, TweetForm, LoginForm
app = Flask(__name__)
app.config['SECRET_KEY'] = "new kkjkesef!"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sesametweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
connect_db(app)


@app.route('/')
def show_all_tweets():
    tweets = Tweet.query.order_by(Tweet.date.desc()).all()
    return render_template('all_tweets.html', tweets=tweets)


@app.route('/authors')
def show_authors():
    characters = Character.query.all()
    return render_template('characters.html', characters=characters)


@app.route('/authors/<int:author_id>')
def show_profile_page(author_id):
    character = Character.query.get_or_404(author_id)
    return render_template('character_profile.html', author=character.author)


@app.route('/hashtags/<string:hashtag_text>')
def show_hashtag_tweets(hashtag_text):
    hashtag = Hashtag.query.get_or_404(hashtag_text)
    return render_template('hashtag.html', hashtag=hashtag)


@app.route('/hashtags')
def show_hashtags():
    hashtags = Hashtag.query.all()
    return render_template('hashtags.html', hashtags=hashtags)


@app.route('/mentions/<string:screen_name>')
def show_mention_tweets(screen_name):
    mention = Mention.query.get_or_404(screen_name)
    return render_template('mention.html', mention=mention)


@app.route('/mentions')
def show_mentions():
    mentions = Mention.query.all()
    return render_template('mentions.html', mentions=mentions)


@app.route('/logout')
def logout():
    if 'author_id' in session:
        session.pop('author_id')

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def handle_register():
    if 'author_id' in session:
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

            session['author_id'] = new_user.author_id

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
            session['author_id'] = user.author_id
            return redirect('/')
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template("login.html", form=form)


@app.route('/authors/<int:author_id>/tweets/new', methods=['GET', 'POST'])
def new_tweet(author_id):
    if 'author_id' in session:

        form = TweetForm()

        if form.validate_on_submit():
            text = form.text.data

            new_tweet = Tweet(text=text,
                              author_id=author_id)
            db.session.add(new_tweet)
            db.session.commit()
            return redirect(f'/authors/{author_id}')
        else:
            return render_template('new_tweet.html', form=form)

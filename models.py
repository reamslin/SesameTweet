from flask_sqlalchemy import SQLAlchemy
import datetime
import GetOldTweets3 as got
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)


class Character(db.Model):
    """Model class for Sesame Street Characters"""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    twitter = db.Column(db.String, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    author = db.relationship('Author')

    def get_tweets(self):
        """get unstored tweets"""
        tweetCriteria = got.manager.TweetCriteria().setUsername(self.twitter)\
            .setMaxTweets(10)
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)

        for tweet in tweets:

            # has tweet already been added? break

            new_tweet = Tweet(twitter_id=tweet.id, text=tweet.text,
                              date=tweet.date, author_id=self.author_id)

            db.session.add(new_tweet)

            db.session.commit()


class Author(db.Model):
    """Model class for Sesame Street Characters"""

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)

    birthday = db.Column(db.Date)

    tweets = db.relationship('Tweet', backref='author')


class User(db.Model):
    """Model class for users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String, nullable=False, unique=True)

    password = db.Column(db.String, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    author = db.relationship('Author')

    @classmethod
    def register(cls, username, password, name):

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode('utf8')

        new_author = Author(name=name)
        db.session.add(new_author)
        db.session.commit()

        new_user = cls(username=username, password=hashed_utf8,
                       author_id=new_author.id)

        db.session.add(new_user)
        db.session.commit()

        return new_user

    @classmethod
    def authenticate(cls, username, password):
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False


class Tweet(db.Model):
    """model class for tweets"""

    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    twitter_id = db.Column(db.String)

    text = db.Column(db.Text, nullable=False)

    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

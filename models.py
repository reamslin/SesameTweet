from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_bcrypt import Bcrypt
import twitter
from secrets import *
import re

bcrypt = Bcrypt()
db = SQLAlchemy()

api = twitter.Api(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token_key=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    cache=None,
    tweet_mode='extended')

num_seed_tweets = 200


def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)


class Character(db.Model):
    """Model class for Sesame Street Characters"""

    __tablename__ = 'characters'

    author_id = db.Column(db.Integer, db.ForeignKey(
        'authors.id'), primary_key=True)

    twitter = db.Column(db.String, nullable=False)

    author = db.relationship('Author')

    def get_timeline(self):
        """get tweets from twitter API"""

        tweets = api.GetUserTimeline(
            screen_name=self.twitter, include_rts=False, exclude_replies=True, trim_user=True, count=num_seed_tweets)
        for tweet in tweets:
            if not tweet.quoted_status:
                new_tweet = Tweet(twitter_id=tweet.id, text=re.sub(r"http\S+", "", tweet.full_text),
                                  date=tweet.created_at, author_id=self.author_id)
                db.session.add(new_tweet)
                db.session.commit()

                if tweet.media:
                    for m in tweet.media:
                        if m.type == 'video':
                            new_media = Media(tweet_id=new_tweet.id, media_type='video',
                                              url=m.video_info.get('variants')[1].get('url'))
                            db.session.add(new_media)
                        elif m.type == 'photo':
                            new_media = Media(
                                tweet_id=new_tweet.id, media_type='photo', url=m.media_url)
                            db.session.add(new_media)

                if tweet.hashtags:
                    for hashtag in tweet.hashtags:
                        hashtag_obj = Hashtag.query.get(hashtag.text)
                        if hashtag_obj:
                            new_tweet.hashtags.append(hashtag_obj)
                        else:
                            new_tweet.hashtags.append(
                                Hashtag(text=hashtag.text))

                    new_tweet.add_hashtag_links()

                db.session.commit()

                if tweet.user_mentions:
                    for mention in tweet.user_mentions:
                        mention_obj = Mention.query.get(mention.screen_name)
                        if mention_obj:
                            new_tweet.mentions.append(mention_obj)
                        else:
                            try:
                                user = api.GetUser(
                                    screen_name=mention.screen_name)
                                new_tweet.mentions.append(
                                    Mention(screen_name=mention.screen_name,
                                            image=user.profile_image_url, banner=user.profile_banner_url,
                                            description=user.description, name=user.name))
                            except:
                                pass

                    new_tweet.add_mention_links()

                db.session.commit()

    def get_user_data(self):
        """get user data from twitter API"""

        user = api.GetUser(screen_name=self.twitter)

        self.author.image = user.profile_image_url
        self.author.banner = user.profile_banner_url
        self.author.description = user.description

        db.session.commit()

    @classmethod
    def register(cls, name, twitter):
        """class method for registering a new character to the system"""

        new_author = Author(name=name, role='Character')
        db.session.add(new_author)
        db.session.commit()
        new_character = Character(twitter=twitter, author_id=new_author.id)
        db.session.add(new_character)
        db.session.commit()

        new_character.get_user_data()
        new_character.get_timeline()

        return new_character


class Author(db.Model):
    """Model class for Sesame Street Characters"""

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    role = db.Column(db.String, nullable=False)

    name = db.Column(db.String, nullable=False)

    image = db.Column(db.String)

    banner = db.Column(db.String)

    description = db.Column(db.Text)

    birthday = db.Column(db.Date)

    tweets = db.relationship('Tweet', backref='author')


class User(db.Model):
    """Model class for users"""

    __tablename__ = 'users'

    author_id = db.Column(db.Integer, db.ForeignKey(
        'authors.id'), primary_key=True)

    username = db.Column(db.String, nullable=False, unique=True)

    password = db.Column(db.String, nullable=False)

    author = db.relationship('Author')

    @classmethod
    def register(cls, username, password, name):

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode('utf8')

        new_author = Author(name=name, role='User')
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

    def add_hashtag_links(self):

        for hashtag in self.hashtags:
            self.text = self.text.replace(
                f'#{hashtag.text}', f'<a href="/hashtags/{hashtag.text}">#{hashtag.text}</a>')

    def add_mention_links(self):
        for mention in self.mentions:
            self.text = self.text.replace(
                f'@{mention.screen_name}', f'<a href="/mentions/{mention.screen_name}">@{mention.screen_name}</a>')

    hashtags = db.relationship('Hashtag',
                               secondary='hashtags_tweets',
                               backref='tweets')
    mentions = db.relationship('Mention',
                               secondary='mentions_tweets',
                               backref='tweets')


class Hashtag(db.Model):
    """model for hashtags"""

    __tablename__ = 'hashtags'

    text = db.Column(db.String, primary_key=True)


class HashtagTweet(db.Model):
    """model for hashtag tweet many-to-many relationship"""

    __tablename__ = 'hashtags_tweets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))

    hashtag_text = db.Column(db.String, db.ForeignKey('hashtags.text'))


class Mention(db.Model):
    """model for mentions"""

    __tablename__ = 'mentions'

    screen_name = db.Column(db.String, primary_key=True, nullable=False)

    name = db.Column(db.String, nullable=False)

    image = db.Column(db.String)

    banner = db.Column(db.String)

    description = db.Column(db.Text)


class MentionTweet(db.Model):
    """model for mention tweet many-to-many relationship"""

    __tablename__ = 'mentions_tweets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))

    mention_screen_name = db.Column(
        db.String, db.ForeignKey('mentions.screen_name'))


class Media(db.Model):
    """model for media"""

    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tweet_id = db.Column(db.Integer, db.ForeignKey(
        'tweets.id'), nullable=False)

    media_type = db.Column(db.String, nullable=False)

    url = db.Column(db.String, nullable=False)

    tweet = db.relationship('Tweet', backref='media')

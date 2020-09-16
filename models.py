from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_bcrypt import Bcrypt
import twitter
from secrets import *
import re
import GetOldTweets3 as got

bcrypt = Bcrypt()
db = SQLAlchemy()

api = twitter.Api(
    consumer_key=os.environ.get('API_KEY')
    consumer_secret=os.environ.get('API_SECRET_KEY')
    access_token_key=os.environ.get('ACCESS_TOKEN')
    access_token_secret=os.environ.get('ACCESS_TOKEN_SECRET'),
    cache=None,
    tweet_mode='extended',
    sleep_on_rate_limit=True)

num_seed_tweets = None


def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)


class Character(db.Model):
    """Model class for Sesame Street Characters"""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    screen_name = db.Column(db.String, nullable=False)

    name = db.Column(db.String, nullable=False)

    image = db.Column(db.String)

    banner = db.Column(db.String)

    description = db.Column(db.Text)

    latest_tweet = db.Column(db.String)

    tweets = db.relationship('Tweet', order_by='Tweet.date')

    def get_timeline(self):
        """get tweets from twitter API"""

        tweetCriteria = got.manager.TweetCriteria().setUsername(
            self.screen_name)
        tweets_got = got.manager.TweetManager.getTweets(tweetCriteria)
        tweet_ids = [tweet.id for tweet in tweets_got]
        tweets = api.GetStatuses(status_ids=tweet_ids, trim_user=True)
        for tweet in tweets:
            Tweet.parse(tweet, self.id)

    def get_user_data(self):
        """get user data from twitter API"""

        user = api.GetUser(screen_name=self.screen_name)

        self.image = user.profile_image_url
        self.banner = user.profile_banner_url
        self.description = user.description

        db.session.commit()

    def update(self):
        self.get_user_data()

        new_tweets = api.GetUserTimeline(
            screen_name=self.screen_name, since_id=self.latest_tweet, trim_user=True, exclude_replies=True, include_rts=False)

        for tweet in new_tweets:
            Tweet.parse(tweet, self.id)
            self.latest_tweet = tweet.id

    @classmethod
    def register(cls, name, screen_name):
        """class method for registering a new character to the system"""

        new_character = Character(screen_name=screen_name, name=name)

        db.session.add(new_character)
        db.session.commit()

        new_character.get_user_data()
        new_character.get_timeline()
        latest_tweet = Tweet.query.filter_by(
            character_id=new_character.id).order_by(Tweet.date.desc()).first()
        new_character.latest_tweet = latest_tweet.twitter_id

        return new_character

    def serialize(self):
        return {
            'id': self.id,
            'screen_name': self.screen_name,
            'name': self.name,
            'image': self.image,
            'banner': self.banner,
            'description': self.description
        }


class Tweet(db.Model):
    """model class for tweets"""

    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    twitter_id = db.Column(db.String)

    text = db.Column(db.Text, nullable=False)

    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.datetime.now)

    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))

    character = db.relationship('Character')

    def add_hashtag_links(self):

        for hashtag in self.hashtags:
            self.text = self.text.replace(
                f'#{hashtag.text}', f'<a href="/hashtags/{hashtag.text}">#{hashtag.text}</a>')

    def add_mention_links(self):
        for mention in self.mentions:
            self.text = self.text.replace(
                f'@{mention.screen_name}', f'<a href="/mentions/{mention.screen_name}">@{mention.screen_name}</a>')

    hashtags = db.relationship('Hashtag',
                               secondary='hashtags_tweets')
    mentions = db.relationship('Mention',
                               secondary='mentions_tweets')

    def serialize(self):
        return {
            'id': self.id,
            'twitter_id': self.twitter_id,
            'text': self.text,
            'month': self.date.month,
            'day': self.date.day,
            'year': self.date.year,
            'character': self.character.serialize(),
            'media': [m.serialize() for m in self.media]
        }

    @classmethod
    def parse(cls, tweet, character_id):
        # ignoring quoted tweets and replies
        if not (tweet.quoted_status or tweet.in_reply_to_screen_name):
            new_tweet = cls(twitter_id=tweet.id, text=re.sub(r"http\S+", "", tweet.full_text),
                            date=tweet.created_at, character_id=character_id)
            db.session.add(new_tweet)
            db.session.commit()

            if tweet.media:
                for m in tweet.media:
                    # animated gifs are stored as videos, play them on loop
                    if m.type == 'video' or m.type == 'animated_gif':
                        new_media = Media(
                            tweet_id=new_tweet.id, media_type=m.type, media_url=m.media_url)
                        db.session.add(new_media)
                        db.session.commit()
                        for v in m.video_info.get('variants'):
                            new_source = Source(media_id=new_media.id, content_type=v.get(
                                'content_type'), url=v.get('url'))
                            db.session.add(new_source)
                    elif m.type == 'photo':
                        new_media = Media(
                            tweet_id=new_tweet.id, media_type='photo', media_url=m.media_url)
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
                                        followers_count=user.followers_count,
                                        image=user.profile_image_url, banner=user.profile_banner_url,
                                        description=user.description, name=user.name))
                        except:
                            pass

                new_tweet.add_mention_links()

            db.session.commit()


class Hashtag(db.Model):
    """model for hashtags"""

    __tablename__ = 'hashtags'

    text = db.Column(db.String, primary_key=True)

    tweets = db.relationship('Tweet',
                             secondary='hashtags_tweets',
                             order_by='Tweet.date.desc()')


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

    followers_count = db.Column(db.Integer)

    tweets = db.relationship('Tweet',
                             secondary='mentions_tweets',
                             order_by='Tweet.date.desc()')


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

    media_url = db.Column(db.String, nullable=False)

    tweet = db.relationship('Tweet', backref='media')

    def serialize(self):
        return {
            'id': self.id,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'sources': [source.serialize() for source in self.sources]
        }


class Source(db.Model):
    """ model for video sources"""

    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    content_type = db.Column(db.String)

    url = db.Column(db.String)

    media = db.relationship('Media', backref='sources')

    def serialize(self):
        return {
            'id': self.id,
            'content_type': self.content_type,
            'url': self.url
        }

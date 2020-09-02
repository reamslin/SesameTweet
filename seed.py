from app import app
from models import db, Tweet, Character, Author


db.drop_all()
db.create_all()

a1 = Author(
    name='Big Bird'
)
db.session.add(a1)
db.session.commit()
c1 = Character(
    twitter='BigBird',
    author_id=a1.id
)

db.session.add(c1)
db.session.commit()

c1.get_tweets()


a2 = Author(
    name='Elmo'
)
db.session.add(a2)
db.session.commit()
c2 = Character(
    twitter='Elmo',
    author_id=a2.id
)


db.session.add(c2)
db.session.commit()

c2.get_tweets()

a3 = Author(
    name='Grover'
)
db.session.add(a3)
db.session.commit()
c3 = Character(
    twitter='grover',
    author_id=a3.id
)

db.session.add(c3)
db.session.commit()

c3.get_tweets()

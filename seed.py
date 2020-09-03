from app import app
from models import db, Tweet, Character, Author


db.drop_all()
db.create_all()

elmo = Character.register(name='Elmo', twitter='elmo')

big_bird = Character.register(name='Big Bird', twitter='bigbird')

grover = Character.register(name='Grover', twitter='grover')

oscar = Character.register(name='Oscar The Grouch', twitter='oscarthegrouch')

bert = Character.register(name='Bert', twitter='bertsesame')

ernie = Character.register(name='Ernie', twitter='sesameernie')

abby = Character.register(name='Abby Cadabby', twitter='abbycadabbysst')

count = Character.register(name='Count Von Count', twitter='countvoncount')

cookie = Character.register(name='Cookie Monster', twitter='mecookiemonster')

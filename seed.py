from app import app
from models import db, Character


db.drop_all()
db.create_all()

sesame_street = Character.register(
    name='Sesame Street', screen_name='sesamestreet')
elmo = Character.register(name='Elmo', screen_name='elmo')

big_bird = Character.register(name='Big Bird', screen_name='bigbird')

grover = Character.register(name='Grover', screen_name='grover')

oscar = Character.register(name='Oscar The Grouch',
                           screen_name='oscarthegrouch')

bert = Character.register(name='Bert', screen_name='bertsesame')

ernie = Character.register(name='Ernie', screen_name='sesameernie')

abby = Character.register(name='Abby Cadabby', screen_name='abbycadabbysst')

count = Character.register(name='Count Von Count', screen_name='countvoncount')

cookie = Character.register(name='Cookie Monster',
                            screen_name='mecookiemonster')

snuffy = Character.register(
    name='Snuffleupagus', screen_name='mrsnuffleupagus')

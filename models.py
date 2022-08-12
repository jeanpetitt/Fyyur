from flask_sqlalchemy import SQLAlchemy
from flask import  Flask
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# creation du model Salle(Venue) 
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(50))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    

    def __repr__(self):
        return f'le lieu de concert {self.name}'
# creation du model artiste(Artist) normalises
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref=db.backref('artist', cascade='all, delete'), lazy=True)
    
    def __repr__(self):
        return f'<artiste {self.name}>'

# creations du model Spectacle(Show)
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('venue', cascade='all, delete'), lazy=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime())
   
    def __repr__(self):
        return f" le spetacle {self.id} aura lieu a {self.start_time} par l'artiste {self.artist_id} a la salle(venue) {self.venue_id}"

# realisation de la relation plusieurs a plusieurs entre artiste et spectacles
# noter que la relation show contient un atribut start time donc il ne sera pas 
#necessaire d'attribuer un tel attribut a cette relation car si on veut ajouter
# il ne faut pas permettre a l'artiste d'entree une heure differente de celle aue possede
# le modele Show car la relation plusieurs a plusieurs a une contrainte temporelle sur le
# fait qu'un spectacle peut avoir plusieurs artistes mais a la meme heure
class ArtistShow(db.Model):
    __tanlename__ = 'artist_show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    artist = db.relationship('Artist', backref="artists")
    show = db.relationship('Show', backref="show")


# creation de la table album pour attribuer les albums aux artistes
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    title_song = db.Column(db.String(120))
    artist = db.relationship('Artist', backref=db.backref('artist', cascade='all, delete'), lazy=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
db.create_all()

# def init_db():
#     db.drop_all()
#     db.create_all()
#    
#     #lg.warning('Database initialized!')

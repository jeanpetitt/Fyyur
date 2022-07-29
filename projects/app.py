#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

#  Create Venue
#  ----------------------------------------------------------------
# creation d'une salle

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue():
    venue = Venue()
    venue_form = VenueForm(obj=venue)
    error = ''
    if request.method == 'POST':
        venue_form = VenueForm(request.form, obj=venue)
        if venue_form.validate():
            venue_form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('venues'))
        else:
            error = venue_form.errors
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('forms/new_venue.html', form=venue_form, error=error)

# routes qui permet d'afficher toutes les salles(venues)
@app.route('/venues')
def venues():
    venues = Venue.query.all()
    data = []
    # obtenir tous les enregistrements distinct(city, state) de maniere distincte
    distinct_city = Venue.query.distinct(Venue.city, Venue.state).all() 
    # pour chaque city_state definissons le format qui sera utiliser
    # pour etre afficher a la vue
    for city_state in distinct_city:
      print(city_state.city, city_state.state)
      data.append(
        {
          'city': city_state.city,
          'state': city_state.state,
          'venues': set()
        }
          # pour la donnees venues de data donnons lui un ens vide ce qui 
          # permettre d'eviter qu'une venue ne soit afficher deux fois pour un meme groupe(city, state)  au cas ou
          # on enregistre cette vunue deux foix dans la bd pour le meme groupe(city, state)
      )  
      # attribuer a chaque groupe(city, state) distinct ses venues
      for venue in venues:
        for venue_data in data:
              if venue.state == venue_data['state'] and venue.city == venue_data['city']:
                venue_data['venues'].add(venue)
 
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# afficher les details sur un lieu(Venue)
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  # creons une liste qui vas stocker les spectacles passes dans les venues correspondante
  past_shows = []
  # creons une liste qui va stocker les spectacles a venir 
  upcoming_shows = []
  temps_courant = datetime.now()
  # obtenir la venue ayant pour id=venue_id
  venues = Venue.query.get(venue_id)
  # filtrer toutes les venues(lieux) dans lesquels les spectacles ont deja eu lieu
  shows = Show.query.filter_by(venue_id=venue_id).all()

  for show in shows:
      data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
          }
      if show.start_time > temps_courant:
        upcoming_shows.append(data)
      else:
        past_shows.append(data)
        
  data={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website_link,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "image_link": venues.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    
    # nbre de spectacles avenir et passes
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

# supprimer une venue
@app.route('/venues/<int:venue_id>/delete')
def delete_venue(venue_id):
      try:
          venue = Venue.query.get(venue_id)
          name = venue.name
          db.session.delete(venue)
          db.session.commit()
          flash('la Venue ' +name+ ' a correctement ete suprimer')
      except:
          flash('une erreur est survenue lors de la suppression')
          db.session.rollback()
      finally:
        db.session.close()
          
      
      return redirect(url_for('venues'))
    
# editer une venue
@app.route('/venues/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit_venue(venue_id):
      venue = Venue.query.get(venue_id)
      venue_form = VenueForm(obj=venue)
      error = ''
      if request.method == 'POST':
          venue_form = VenueForm(request.form, obj=venue)
          if venue_form.validate():
                venue_form.populate_obj(venue)
                db.session.add(venue)
                db.session.commit()
                flash('Venue ' + request.form['name'] + ' was successfully Updated!')
                return redirect(url_for('venues'))
          else:
                error = venue_form.errors
      
      return render_template('forms/edit_venue.html', form=venue_form, venue=venue, error=error)



#  Artists
#  ----------------------------------------------------------------
# creer un artist

@app.route('/artists/create', methods=['POST', 'GET'])
def create_artist_submission():
    artist = Artist()
    artist_form = ArtistForm(obj=artist)
    error = ''
    if request.method == 'POST':
        artist_form = ArtistForm(request.form, obj=artist)
        if artist_form.validate():
            artist_form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('artists'))
        else:
            error = artist_form.errors
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('forms/new_artist.html', form=artist_form, error=error)

# afficher la listee d'artiste
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = artists
    return render_template('pages/artists.html', artists=data)

# afficher les details sur un artiste
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # creons une liste qui vas stocker les spectacles passes dans les venues correspondante
  past_shows = []
  # creons une liste qui va stocker les spectacles a venir 
  upcoming_shows = []
  temps_courant = datetime.now()
  # obtenir la venue ayant pour id=venue_id
  artists = Artist.query.get(artist_id)
  # filtrer toutes les artist et les lieux ou ils ferons des spectacles ou qu'ils ont
  # fait des spectacles
  shows = Show.query.filter_by(artist_id=artist_id).all()

  for show in shows:
      data = {
            "artist_id": show.artist_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
          }
      if show.start_time > temps_courant:
        upcoming_shows.append(data)
      else:
        past_shows.append(data)
  
  data={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
 
  return render_template('pages/show_artist.html', artist=data)

# recherche d'un artiste
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Update artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist_form = ArtistForm(obj=artist)
  error = ''
  if request.method == 'POST':
        artist_form = ArtistForm(request.form, obj=artist)
        if artist_form.validate():
            artist_form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully update!')
            return redirect(url_for('artists'))
        else:
            error = artist_form.errors
  
  return render_template('forms/edit_artist.html', form=artist_form, artist=artist, error=error)

# supprimer un artist
@app.route('/artists/<int:artist_id>/delete')
def delete_artist(artist_id):
      try:
          artist = Artist.query.get(artist_id)
          name = artist.name
          db.session.delete(artist)
          db.session.commit()
          flash("l'artiste " +name+ ' a correctement ete suprimer')
      except:
          flash('une erreur est survenue lors de la suppression')
          db.session.rollback()
      finally:
        db.session.close()
          
      
      return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      shows = Show.query.all()
      data = []
      new_data = []
      for show in shows:
            data.append({
              'venue_id': show.venue_id,
              'venue_name': show.venue.name,
              'artist_id': show.artist_id,
              'artist_name': show.artist.name,
              'artist_image_link': show.artist.image_link,
              'start_time': format_datetime(str(show.start_time))
            })
      # eliminer les doublons
      for item in data:
            if item not in new_data:
                  new_data.append(item)
      data = new_data
      return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['POST', 'GET'])
def create_shows():
  show = Show()
  show_form = ShowForm(obj=show)
  error = ''
  artist = Artist.query.all()
  artist_id = []
  for id in artist:
        artist_id.append(id)
  if request.method == 'POST':
        show_form = ShowForm(request.form, obj=show)
        if show_form.validate():
              show_form.populate_obj(show)
              db.session.add(show)
              db.session.commit()
              flash('Show was successfully listed!')
              return redirect(url_for('shows'))
        else:
              error = show_form.errors
        
  return render_template('forms/new_show.html', form=show_form, error=error)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

"""
# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
"""
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000)

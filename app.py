#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from crypt import methods
import json
from dateutil.parser import parse
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

# app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# @app.cli.command()
# def init_db():
#     models.init_db()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='fr')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # liste des lieux et artistes a afficher sur la page d'accueil
  venues = Venue.query.limit(10).all()
  artists = Artist.query.limit(10).all()    
  
  return render_template('pages/home.html', venues=venues,  artists=artists)


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
      
  terme = request.form.get('search_term', '')
  # la recherche s'effectuera en fonction du nom de la venue
  # nous allons filtrer les resultats en fonction de ce que l'utilisateateur va saisir
  # pour cela nous alons utilser ilike similaire a icontains en django pour la sensibilite
  # a la casse, il y'aura pas de difference entre A et a
  res = Venue.query.filter(Venue.name.ilike(f'%{terme}%'))
  
  response={
    "count": res.count(),
    "data": res
  }
  return render_template('pages/search_venues.html', results=response, search_term=terme)

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
    num_tel = ''
    if request.method == 'POST':
        artist_form = ArtistForm(request.form, obj=artist)
        phone = request.form.get('phone')
        if artist_form.validate():
            artist_form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('artists'))
        else:
            num_tel = phone
            error = artist_form.errors
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('forms/new_artist.html', form=artist_form, error=error, num_tel=num_tel)

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
  
  # lister les album et les chansons d'un artiste
  album_distinct = Album.query.distinct(Album.name).limit(10).all()
  list_album = Album.query.all()
  albums = []
  for alb in album_distinct:
        albums.append({
          'name': alb.name,
          'artist_image_link': alb.artist.image_link,
          'list_song': set()
        })
  for album in list_album:
        for item in albums:
            if album.name == item['name']:
                item['list_song'].add(album)
                  

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
 
  return render_template('pages/show_artist.html', artist=data, albums=albums)

# recherche d'un artiste
@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  # recherche d'un artiste en foncton du nom nom sensible a la casse
  terme = request.form.get('search_artist', '')
  res = Artist.query.filter(Artist.name.ilike(f'%{terme}%'))
  
  response={
    "count": res.count(),
    "data": res
  }
  return render_template('pages/search_artists.html', results=response, search_term=terme)

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

# rechercher un artiste etant sur la page de lieu
@app.route('/search_venue/artist', methods=['POST'])
def search_artit_venue():
  terme = request.form.get('search_artist', '')
  res = Artist.query.filter(Artist.name.ilike(f'%{terme}%'))
  
  response={
    "count": res.count(),
    "data": res
  }
  return render_template('pages/search_artist_venue.html', results=response, search_term=terme)

# fonction permettant d'ajouter un artiste a un spectacle
@app.route('/artist/show/<int:artist_id>', methods=['GET','POST'])
def add_show_artist(artist_id):
        artist = Artist.query.get(artist_id)
        artist_show = ArtistShow()
        form = ArtistShowForm(obj=artist_show)
        if request.method == 'POST':   
             form = ArtistShowForm(request.form, obj=artist_show)
             if form.validate:
                    form.populate_obj(artist_show)
                    db.session.add(artist_show)
                    db.session.commit()
                    flash("l'artiste "+artist.name+" a ete ajoute avec succes au  spectacle")
                    return redirect(url_for('shows'))
        return render_template('forms/add_artist_show.html', artist=artist)
      

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      shows = Show.query.all()
      show_artists = ArtistShow.query.all()
      # afficher tous les artistes d'un spectacle car il s'agit d'une relation
      # plusieurs a plusieurs
      data = []
      new_data = []
      artists = Artist.query.all()
      for show in shows: 
            data.append({
                          'show_id': show.id,
                          'venue_id': show.venue_id,
                          'venue_name': show.venue.name,
                          'artists': set(),                
                          'venue_image_link': show.venue.image_link,
                          'start_time': str(show.start_time)
                        }) 
            for artist in artists:
              for show_art in show_artists:
                if artist.id == show_art.artist.id and show.id == show_art.show_id:
                    for item in data:
                      if item['show_id'] == show.id:
                          item['artists'].add(artist)                                    
                        
      # eliminer les doublons
      for item in data:
            if item not in new_data:
                  new_data.append(item)
      data = new_data
      return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['POST', 'GET'])
def create_shows():
  show = Show()
  artistShow = ArtistShow()
  show_form = ShowForm(obj=show)
  artistShow_form = ArtistShowForm(obj=artistShow)
  error = ''
  if request.method == 'POST':
        artistShow_form = ArtistShowForm(request.form, obj=artistShow)
        show_form = ShowForm(request.form, obj=show)
        
        if show_form.validate() and  artistShow_form.validate():
              show_form.populate_obj(show)
              db.session.add(show)
              db.session.commit()
              # correspndre l'id du du spectacle creer a la classe d'association
              # artistShow
              artistShow_form.populate_obj(artistShow)
              artistShow.show_id = show.id
              db.session.add(artistShow)
              db.session.commit()  
              flash('Show was successfully listed!')
              return redirect(url_for('shows'))
        else:
              error = show_form.errors
        
  return render_template('forms/new_show.html', form=show_form, form1=artistShow_form)

@app.route('/albums/create', methods=['POST', 'GET'])
def albums():
      album = Album()
      form = AlbumForm(obj=album)
      error = ''
      if request.method == 'POST':
            form = AlbumForm(request.form, obj=album)
            if form.validate():
                  form.populate_obj(album)
                  db.session.add(album)
                  db.session.commit()
                  flash('album was succesfully listed')
                  return redirect(url_for('index'))
            else:
                  error = form.errors
                
      return render_template('forms/new_album.html', form=form)

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
    app.run()
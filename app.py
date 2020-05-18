#-------- --------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel , sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)



# TODO: connect to as local postgresql database
migrate =Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
	__tablename__ = 'Venue'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	city = db.Column(db.String(120), nullable=False)
	state = db.Column(db.String(120), nullable=False)
	address = db.Column(db.String(120), nullable=False)
	phone = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	genres = db.Column("genres", db.ARRAY(db.String(250)), nullable=False)
	facebook_link = db.Column(db.String(120))
	website = db.Column(db.String(250))
	seeking_talent = db.Column(db.Boolean, default=True)
	seeking_description = db.Column(db.String(250))
	shows = db.relationship('Show', backref='venue', lazy=True)
	def __repr__(self):
		return f'<Venue {self.id}, {self.name}, {self.city},\
                        {self.state}, {self.address}, {self.phone},\
                        {self.image_link},{self.genres},{self.facebook_link}, \
                        {self.website}, {self.seeking_talent}, {self.seeking_description}>'

class Artist(db.Model):
	__tablename__ = 'Artist'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	city = db.Column(db.String(120), nullable=False)
	state = db.Column(db.String(120), nullable=False)
	phone = db.Column(db.String(120))
	website = db.Column(db.String(250))
	genres = db.Column("genres", db.ARRAY(db.String(250)), nullable=False)
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	seeking_venue = db.Column(db.Boolean, default=True)
	seeking_description = db.Column(db.String(250))
	shows = db.relationship('Show', backref='artist', lazy=True)	
	def __repr__(self):
		return f'<Artist{self.id}, {self.name}, {self.city}, {self.state},\
	                    {self.phone}, {self.website}, {self.genres} ,\
	                    {self.image_link} , {self.facebook_link},\
	                    {self.seeking_venue}, { self.seeking_description}>'

class Show(db.Model):
				__tablename__ = 'Show'
				id = db.Column(db.Integer, primary_key=True)
				artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
				venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
				start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
				def __repr__(self):
						return f'<Show artist_id :{self.artist_id}, venue_id {self.venue_id}, start_time {self.start_time}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
		format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
		format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)
 app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
	return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
	item_venue = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
	data = [] #resoure https://flaskage.readthedocs.io/en/latest/database_queries.html


	for item in all_venue: # check all veneue by cites,states
		all_venues = Venue.query.filter_by(state=item.state).filter_by(city=item.city).all()
		venue_data = []
		for venue in item_venue:
			venue_data.append({
			"id": venue.id,
			"name": venue.name,  
			"num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
			})

		data.append({ 
			"city": item.city,
			"state": item.state, 
			"venues": venue_data
			})

		return render_template('pages/venues.html', areas=data)

#------------------ search venue -------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
	search_term = request.form.get('search_term', '')
	result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
	response={ #ilike source =https://www.postgresqltutorial.com/postgresql-like/
		"count": result.count(),  
		"data": result
	 }
		
	
	return render_template('pages/search_venues.html', results=response, search_term=search_term)

#------------------------venue by id --------------------------------

@app.route('/venues/<int:venue_id>')

def show_venue(venue_id):
	upcoming_shows_all= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
	upcoming_shows = []# store upcoming show # join artist , show 
	
	past_shows_all = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
	past_shows = []  # store past show

	for show in upcoming_shows_all:
		upcoming_shows.append({
			"artist_id": show.artist_id,
			"artist_name": show.artist.name,
			"artist_image_link": show.artist.image_link,
			"start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
		 })

	for show in past_shows_all:
		past_shows.append({
			"artist_id": show.artist_id,
			"artist_name": show.artist.name,
			"artist_image_link": show.artist.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		 })

	data = {
		"id": venue.id,
		"name": venue.name,
		"city": venue.city,
		"state": venue.state,
		"genres": venue.genres,
		"address": venue.address,
		"phone": venue.phone,
		"website": venue.website,
		"facebook_link": venue.facebook_link,
		"image_link": venue.image_link,
		"seeking_talent": venue.seeking_talent,
		"seeking_description": venue.seeking_description,
		"upcoming_shows": upcoming_shows,
		"upcoming_shows_count": len(upcoming_shows),
		"past_shows": past_shows,
		"past_shows_count": len(past_shows),
		}
	return render_template('pages/show_venue.html', venue=single_venue)

#  --------------------------create venue --------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	form = VenueForm()
	error =False
	try:
		# get form data and create 
		newVenue = Venue(
		name = request.form['name'],
		city = request.form['city'],
		state = request.form['state'],
		address = request.form['address'],
		phone = request.form['phone'],
		genres = request.form.getlist('genres'),
		facebook_link = request.form['facebook_link'])
		# commit session to database
		db.session.add(newVenue)
		db.session.commit()
		# flash success 
		flash('Venue ' + request.form['name'] + ' was successfully listed!')
	except:
		error = True
		db.session.rollback()
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
	finally:
		# closes session
		db.session.close()
	return render_template('pages/home.html')

		# TODO: on unsuccessful db insert, flash an error instead.
		# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#---------------------------delete ------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	venue_obj = Venue.query.get(venue_id)
	try:
		for genres in venue_obj.genres:
			db.session.delete(genres)
			db.session.delete(venue_obj)
			db.session.comit()
	except SQLAlchemyError as e:
			print(e)
	return None
#  -------------------------- read artis --------------------------------------
@app.route('/artists')
def artists():
	artist = Artist.query.all() # read all  artist 
	data = []
	if len(artist) > 0: # count length artist 
		for item in artist:
			data.append({"id": item.id, "name": item.name})
	return render_template('pages/artists.html', artists=data)
#------------------------------- search artist ----------------------------------
@app.route('/artists/search', methods=['POST'])
	def search_artists():
	search_term = request.form.get('search_term', '')
	results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
	#ilike sources =https://www.postgresqltutorial.com/postgresql-like/
	data = []
	for result in results:
		data.append({
			"id": result.id,
			"name": result.name,
			"num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
		 })

		response={
				"count": len(results),
				"data": data
		 }

		response["data"].append({"id": item.id, "name": item.name, "num_upcoming_shows": show_count})
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#-------------------------------artist by id------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	artist_query = db.session.query(Artist).get(artist_id)
	past_shows_all= db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
	past_shows = []

	upcoming_shows_all = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
	upcoming_shows = []

	for show in past_shows_all:
		past_shows.append({
		    "venue_id": show.venue_id,
			"venue_name": show.venue.name,
			"artist_image_link": show.venue.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')

		 })


	for show in upcoming_shows_all:
		upcoming_shows.append({
			"venue_id": show.venue_id,
			"venue_name": show.venue.name,
			"artist_image_link": show.venue.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		 })

	data = {
		"id": artist_query.id,"name": artist_query.name,"genres": artist_query.genres,
		"city": artist_query.city,"state": artist_query.state,
		"phone": artist_query.phone,"website": artist_query.website,
		"facebook_link": artist_query.facebook_link,"seeking_venue": artist_query.seeking_venue,
		"seeking_description": artist_query.seeking_description,"image_link": artist_query.image_link,
		"past_shows": past_shows,"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
		 }

	return render_template('pages/show_artist.html', artist=data)


#  -----------------------------Update-----------------------------------
#----------------------------venue id edit   get --------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
		form = ArtistForm()
		artist = Artist.query.get(artist_id) # get query to retlive venue 

		if artist: 
				form.name.data = artist.name
				form.city.data = artist.city
				form.state.data = artist.state
				form.phone.data = artist.phone
				form.genres.data = artist.genres
				form.facebook_link.data = artist.facebook_link
				form.image_link.data = artist.image_link
				form.website.data = artist.website
				form.seeking_venue.data = artist.seeking_venue
				form.seeking_description.data = artist.seeking_description

		return render_template('forms/edit_artist.html', form=form, artist=artist)
#-------------------------------- venue id get ---------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
		form = VenueForm()
		venue = Venue.query.get(venue_id) # get query to retlive venue 
		
		if venue: 
				form.name.data = venue.name
				form.city.data = venue.city
				form.state.data = venue.state
				form.phone.data = venue.phone
				form.address.data = venue.address
				form.genres.data = venue.genres
				form.facebook_link.data = venue.facebook_link
				form.image_link.data = venue.image_link
				form.website.data = venue.website
				form.seeking_talent.data = venue.seeking_talent
				form.seeking_description.data = venue.seeking_description
		
		return render_template('forms/edit_venue.html', form=form, venue=venue)
#--------------------------------edit venue post -----------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id): 
		venue = Venue.query.get(venue_id)
		error = False 
		try: 
			venue.name = request.form['name']
			venue.city = request.form['city']
			venue.state = request.form['state']
			venue.address = request.form['address']
			venue.phone = request.form['phone']
			venue.genres = request.form.getlist('genres')
			venue.image_link = request.form['image_link']
			venue.facebook_link = request.form['facebook_link']
			venue.website = request.form['website']
			venue.seeking_talent = True if 'seeking_talent' in request.form else False 
			venue.seeking_description = request.form['seeking_description']
			db.session.commit()
			flash(f'Venue was successfully updated!')
		except: 
			error = True
			db.session.rollback()
			print(sys.exc_info())
			flash(f'An error occurred. Venue could not be changed.')
		finally: 
			# close session 
			db.session.close()
			flash(f'Venue was successfully updated!')
		return redirect(url_for('show_venue', venue_id=venue_id))

#  ---------------------------Create Artist-------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
		form = ArtistForm()
		return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
			form =ArtistForm()
			error =False
			try:
				# get form data and create 
				newArtist = Artist(
				name = request.form['name'],
				city = request.form['city'],
				state = request.form['state'],
				address = request.form['address'],
				phone = request.form['phone'],
				genres = request.form.getlist('genres'),
				facebook_link = request.form['facebook_link'])
				# commit session to database
				db.session.add(newArtist)
				db.session.commit()
				# flash success 
				flash('Artist ' + request.form['name'] + ' was successfully listed!')
			except:
				# catches errors
				error =True
				db.session.rollback()
				flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
			finally:
				# closes session
				db.session.close()
		        # on successful db insert, flash success
				flash('Artist ' + request.form['name'] + ' was successfully listed!')
	# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
				return render_template('pages/home.html')

#  --------------------------------Shows--------------------------------
@app.route('/shows')

def shows(): # join tables show, artist ,venue 
		shows_query = db.session.query(Show).join(Artist).join(Venue).all()
		data = [] # store result 

		for show in shows_query: 
				data.append({
					"venue_id": show.venue_id,
					"venue_name": show.venue.name,
					"artist_id": show.artist_id,
					"artist_name": show.artist.name, 
					"artist_image_link": show.artist.image_link,
					"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')

				 })

		return render_template('pages/shows.html', shows=data)

#-------------------------- create shows----------------------------

@app.route('/shows/create')
def create_shows():
		form = ShowForm() # get form data
		return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
				try:
					artist_id = request.form["artist_id"]
					venue_id = request.form["venue_id"]
					start_time = datetime.strptime(request.form["start_time"], '%Y-%m-%d %H:%M:%S')
					show = Show(
						venue_id=venue_id,
						artist_id=artist_id,
						start_time=start_time,
						end_time=start_time + dt.timedelta(hours=60)
						)
								# commit session to database 
								db.session.add(show)
								db.session.commit()
								# on successful db insert, flash success
								flash('Show was successfully listed!')
								return render_template('pages/home.html')
				except SQLAlchemyError as e:
					print(e)
					db.session.rollback()
					flash('Show was not listed!')
					return render_template('errors/404.html')
				finally:
					# close session
					db.session.close()
					return render_template('pages/home.html')
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

# Default port:
if __name__ == '__main__':
				app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
				port = int(os.environ.get('PORT', 5000))
				app.run(host='0.0.0.0', port=port)
'''

import spotipy

class MySpotify:

	def __init__(self,token):
		self.token = token
		self.sp = spotipy.Spotify(auth=self.token)

	def get_user_details(self):
		'''
		Returns a dict of user details
		'''
		user_locale = self.sp.current_user()['country']
		user_name = self.sp.current_user()['display_name']
		user_email = self.sp.current_user()['email']
		user_spotify_id = self.sp.current_user()['id']
		user_product = self.sp.current_user()['product']
		user_followers = self.sp.current_user()['followers']['total']
		user_spotify_link = self.sp.current_user()['external_urls']['spotify']

		user_details = {
		'user_locale':user_locale,
		'user_name':user_name,
		'user_email':user_email,
		'user_spotify_id':user_spotify_id,
		'user_product':user_product,
		'user_followers':user_followers,
		'user_spotify_link':user_spotify_link
		}

		return user_details



	def create_playlist(self,playlist_name,is_public=True):
		'''
		Creates playlist
		Returns Id of created playlist
		'''
		user_spotify_id = self.sp.current_user()['id']
		new_playlist = self.sp.user_playlist_create(user_spotify_id,playlist_name,public=is_public)

		return new_playlist['id']


	def get_user_playlists(self):


		return self.sp.current_user_playlists()



	def get_top_tracks(token,limit=20,time_range='medium_term'):
		'''
		Returns a list of tracks Ids
		time_range can be short_term, medium_term, long_term
		'''

		user_top_tracks = self.sp.current_user_top_tracks(limit=limit,time_range=time_range)
		top_tracks = user_top_tracks['items']
		top_track_ids = []

		for top_track in top_tracks:
			top_track_ids.append(top_track['id'])

		return top_track_ids


	def add_tracks_to_playlist(token,playlist_id,track_ids):
		'''
		Adds tracks to a given playlist
		track_ids is a list
		'''
		sp = spotipy.Spotify(auth=token)
		user_spotify_id = sp.current_user()['id']
		add_tracks = sp.user_playlist_add_tracks(user_spotify_id,playlist_id,track_ids)



	def replace_tracks_in_playlist(token,playlist_id,track_ids):
		'''
		Replace tracks in a given playlist
		track_ids is a list
		'''

		sp = spotipy.Spotify(auth=token)
		user_spotify_id = sp.current_user()['id']
		add_tracks = sp.user_playlist_replace_tracks(user_spotify_id,playlist_id,track_ids)


	def get_recommended_tracks(token,seed_artists=[],seed_genres=[],seed_tracks=[],limit=20):
		'''
		Returns Track Ids
		Seed_artists, seed_tracks are list of Ids
		Seed_genres is name of genre
		At least one of the above 3 is needed
		limit default is 20
		Country is set to current user's locale
		'''

		sp = spotipy.Spotify(auth=token)
		country = sp.current_user()['country']
		recommended_tracks = sp.recommendations(seed_artists,seed_genres,seed_tracks,limit,country)

		recommended_track_ids = []
		for track in recommended_tracks['tracks']:
			recommended_track_ids.append(track['id'])

		return recommended_track_ids
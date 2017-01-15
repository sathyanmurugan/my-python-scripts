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
		user_id = self.sp.current_user()['id']
		user_product = self.sp.current_user()['product']
		user_followers = self.sp.current_user()['followers']['total']
		user_spotify_link = self.sp.current_user()['external_urls']['spotify']

		user_details = {
		'user_locale':user_locale,
		'user_name':user_name,
		'user_email':user_email,
		'user_id':user_id,
		'user_product':user_product,
		'user_followers':user_followers,
		'user_spotify_link':user_spotify_link
		}

		return user_details


	def get_user_playlist_ids(self):
		'''
		Returns playlist Ids
		'''
		playlists = self.sp.current_user_playlists()
		playlist_ids = [pl['id'] for pl in playlists['items']]

		return playlist_ids

	def get_track_ids_from_playlist(self,user_id,playlist_id):


		tracks = self.sp.user_playlist_tracks(user_id,playlist_id)
		track_ids = [track['track']['id'] for track in tracks['items']]

		return track_ids

	def get_recommendations(self,track_ids,country,limit=20):

		recommended_tracks = self.sp.recommendations(seed_tracks=track_ids, country=country, limit=limit)
		recommended_track_ids = [track['id'] for track in recommended_tracks['tracks']]

		return recommended_track_ids

	def replace_tracks_in_playlist(self,user_id,playlist_id,track_ids):
		
		result = self.sp.user_playlist_replace_tracks(user_id,playlist_id,track_ids)

		return result
import spotipy
import spotipy.oauth2 as oauth2
import json
import os
import random


def dump_token(path_to_dir,u_id):
	file_path = os.path.join(path_to_dir,'{0}_token.json'.format(u_id))
	with open(file_path, 'w') as f:
		json.dump(token_data,f)

def get_all_users(path_to_file):
		with open(path_to_file,'r') as f:
			all_user_data = json.load(f)
			user_ids = [user['u_id'] for user in all_user_data]
		return user_ids	

def user_setup(access_token,path_to_dir)

class UserSetup:
	def __init__(self,token_data,path_to_dir):
		
		self.path_to_dir = path_to_dir
		self.sp = spotipy.Spotify(auth=access_token)
		self.u_id = self.sp.current_user()['id']

	def _create_playlist(self):
		
		playlist = self.sp.user_playlist_create(self.u_id,self.playlist_name,public=True)
		user_data = {'u_id':self.u_id,'p_id':playlist['id']}

		return user_data

	def _write_user_to_file(self,user_data):
		file = os.path.join(self.path_to_dir,'all_user_data.json')

		with open(file,'r') as f:
			all_user_data = json.load(f)
		all_user_data.append(user_data)

		with open(file,'w') as f:
			json.dump(all_user_data,f)


class TrackFactory:
	
	def __init__(self,client_id,client_secret,redirect_uri,path_to_token,scope):

		self.auth = oauth2.SpotifyOAuth(
			client_id=client_id,
		    client_secret=client_secret,
		    redirect_uri=redirect_uri,
		    cache_path=path_to_token,
		    scope=scope
		    )

		token_info = self.auth.get_cached_token()
		access_token = token_info['access_token']
		self.sp = spotipy.Spotify(auth=access_token)
		self.u_id = self.sp.current_user()['id']
		#self.u_locale = self.sp.current_user()['country']


	def _get_seed_tracks(self):

		top_tracks = self.sp.current_user_top_tracks(limit=50, time_range='short_term')
		top_track_ids = [track['id'] for track in top_tracks['items']]

		return random.sample(top_track_ids,5)


	def _get_recommendations(self,top_5_tracks):
		
		recommended_tracks = self.sp.recommendations(
			seed_tracks=top_5_tracks,
			#country=self.u_locale
			)
		recommended_track_ids = [track['id'] for track in recommended_tracks['tracks']]

		return recommended_track_ids

	def add_tracks(self,playlist_id):

		seed = self._get_seed_tracks()
		recommendations = self._get_recommendations(seed)
		self.sp.user_playlist_replace_tracks(self.u_id,playlist_id,recommendations)


	def get_user_playlist_ids(self,limit=50,offset=0):
		playlists = self.sp.current_user_playlists(limit=limit,offset=offset)
		playlist_ids = [pl['id'] for pl in playlists['items']]

		#Max returned ids per call is 50.
		#The offset serves as an index, so if the total is higher than 
		#the limit, we can offset the index and query the remaining records
		while len(playlist_ids) < playlists['total']:
			offset+=limit
			playlists = self.sp.current_user_playlists(limit=limit,offset=offset)
			playlist_ids.extend([pl['id'] for pl in playlists['items']])

		return playlist_ids

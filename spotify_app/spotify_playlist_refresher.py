import spotipy.oauth2 as oauth2
import os
import json
from spotify_helper import SongSpotting

data_dir = os.path.join(os.getcwd(),'json_files')
cred_file = os.path.join(data_dir,'spotify_credentials.json')
user_data_file = os.path.join(data_dir,'all_user_data.json') 

#Get Credentials
with open(cred_file,'r') as f:
	c = json.load(f)
s_id = c['spotify_client_id']
s_secret = c['spotify_client_secret']
s_redir = c['spotify_redirect_uri']
s_scope = c['spotify_scope']

#Get all users
with open(user_data_file, 'r') as f:
	users = json.load(f)

updated_user_data = []
for user in users:

	#Connect using user's token and refresh the access token
	path_to_token = os.path.join(data_dir,user['u_id'] + '_token.json')
	auth = oauth2.SpotifyOAuth(
		client_id=s_id,
		client_secret=s_secret,
		redirect_uri=s_redir,
		cache_path=path_to_token,
		scope=s_scope)
	access_token = auth.get_cached_token()['access_token']
	
	#Initliaze user using new access token
	ss = SongSpotting(access_token)

	#Get all playlists of the user and check if our playlist still exists
	#If exists, add user to updated_user_data
	#The idea is to remove users from the user_data file that have deleted their playlist
	p_ids = ss.get_user_playlist_ids()
	if user['p_id'] not in p_ids:
		continue
	updated_user_data.append(user)

	#Generate new songs and add to playlist
	ss.refresh_playlist(playlist_id=user['p_id'])

#Store the users data
with open(user_data_file,'w') as f:
	json.dump(updated_user_data,f)


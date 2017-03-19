from spotify_helper import TrackFactory
import os
import json

data_dir = r'C:\Users\Sathyan\Documents\GitHub\my-python-scripts\spotify_app\json_files'
app_credentials_file = os.path.join(data_dir,'spotify_app_credentials.json')
user_data_file = os.path.join(data_dir,'all_user_data.json') 

#Get Credentials from JSON file
with open(app_credentials_file,'r') as f:
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
	#Connect using user's token
	s_token = os.path.join(data_dir,user['u_id'] + '_token.json')
	tf = TrackFactory(s_id,s_secret,s_redir,s_token,s_scope)

	#Get all playlists of the user and check if our playlist still exists
	#If exists, add user to updated_user_data
	p_ids = tf.get_user_playlist_ids()
	if user['p_id'] not in p_ids:
		continue
	updated_user_data.append(user)

	#Generate new songs and add to playlist
	tf.add_tracks(user['p_id'])

with open(user_data_file,'w') as f:
	json.dump(updated_user_data,f)


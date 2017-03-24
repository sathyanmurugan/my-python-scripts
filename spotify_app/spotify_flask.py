from flask import Flask,redirect,request,render_template
import spotipy.oauth2 as oauth2
from spotify_helper import SongSpotting
import os
import json

app = Flask(__name__,static_folder='static',template_folder='templates')

cred_file = os.path.join(os.getcwd(),'json_files','spotify_credentials.json')
with open(cred_file,'r') as f:
	c = json.load(f)
s_id = c['spotify_client_id']
s_secret = c['spotify_client_secret']
s_redir = c['spotify_redirect_uri']
s_scope = c['spotify_scope']

#Initialize the Auth class to enable user registration/login
auth = oauth2.SpotifyOAuth(
	client_id=s_id,
	client_secret=s_secret,
	redirect_uri=s_redir,
	scope=s_scope)

@app.route('/')
def hello():
	return render_template('welcome.html')

#Visiting this link redirects user to Spotify to confirm scopes
@app.route('/connect')
def connect():
	auth_url = auth.get_authorize_url()
	return redirect(auth_url)

#Redirect from Spotify
@app.route('/main')
def main():

	code = auth.parse_response_code(request.url)
	token_data = auth.get_access_token(code)
	access_token = token_data['access_token']

	ss = SongSpotting(access_token)
	ss.store_token(token_data)
	all_users = ss.get_all_users()
	
	if ss.u_id not in all_users:
		p_id = ss.setup_user()
	
	else:
		#Check if SongSpotting playlist exists among user's playlist
		p_id = ss.get_user_ss_playlist_id()
		p_ids = ss.get_user_playlist_ids()

		# If not, reinitialize user 
		if p_id not in p_ids:
			ss.delete_user()
			p_id = ss.setup_user()
			
	return render_template(
		'main.html',
		user_id=ss.u_id,
		playlist_id=p_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
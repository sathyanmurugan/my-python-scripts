from flask import Flask,redirect,request,render_template
import spotipy
import spotipy.oauth2 as oauth2
from spotify_helper import dump_token
import os
import json

app = Flask(
	__name__,
	static_folder='static',
    template_folder='templates'
)

data_dir = os.path.join(os.getcwd(),'json_files')

#Get Credentials from JSON file
with open(os.path.join(data_dir,'spotify_credentials.json'),'r') as f:
	c = json.load(f)
s_id = c['spotify_client_id']
s_secret = c['spotify_client_secret']
s_redir = c['spotify_redirect_uri']
s_scope = c['spotify_scope']

#Initialize the Auth class to enable user registration/login
auth = oauth2.SpotifyOAuth(client_id=s_id,client_secret=s_secret,redirect_uri=s_redir,scope=s_scope)

@app.route('/')
def hello():
	return render_template('welcome.html')

#Visiting this link redirects user to Spotify to confirm scopes
@app.route('/connect')
def connect():
	auth_url = auth.get_authorize_url()
	return redirect(auth_url)

#Redirect from Spotify
@app.route('/check_user')
def check_user():

	code = auth.parse_response_code(request.url)
	token_data = auth.get_access_token(code)
	access_token = token_data['access_token']

	sp = spotipy.Spotify(auth=access_token)
	u_id = sp.current_user()['id']

	all_users = get_all_users(os.path.join(data_dir,'all_user_data.json'))
	if u_id not in all_users:
		

	dump_token(data_dir,u_id)
	return redirect('/main')


@app.route('/main')
def main():
	
	tf = TrackFactory(s_id,s_secret,s_redir,,s_scope)
	return render_template('main.html')


#After confirmation of scopes, user is redirected to this page 
#Once here, 
#	1. The token is stored as a JSON file, format -> (userid_token.json)
#	2. A playlist is created
#	3. The Id of the playlist and the UserId is appended to the all_user_data.json file

@app.route('/user_setup')
def user_setup():

	#Get token
	token_info = auth.get_token(request.url)
	#Setup user with playlist and create JSONs
	setup = UserSetup(token_info,data_dir)
	response,u_id,p_id = setup.setup()

	#Generate songs in playlist
	token_file_name = u_id + '_token.json'
	path_to_token = os.path.join(data_dir,token_file_name)
	track_factory = TrackFactory(s_id,s_secret,s_redir,path_to_token,s_scope)
	track_factory.add_tracks(p_id)
	
	return response


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
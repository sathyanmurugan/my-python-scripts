from flask import Flask,redirect,request
from spotify_helper import AuthFlow,UserSetup,TrackFactory
import os
import json

app = Flask(__name__)
data_dir = r'C:\Users\Sathyan\Documents\GitHub\my-python-scripts\spotify_app\json_files'

#Get Credentials from JSON file
with open(os.path.join(data_dir,'spotify_credentials.json'),'r') as f:
	c = json.load(f)
s_id = c['spotify_client_id']
s_secret = c['spotify_client_secret']
s_redir = c['spotify_redirect_uri']
s_scope = c['spotify_scope']

#Initialize the AuthFlow class to enable user registration
auth = AuthFlow(s_id,s_secret,s_redir,s_scope)

#Visiting this link redirects user to Spotify to confirm scopes
@app.route('/')
def hello():
	auth_url = auth.get_auth_url()
	return redirect(auth_url)

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
    app.run(host='0.0.0.0',port=8080)
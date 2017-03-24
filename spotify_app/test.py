import spotipy
import spotipy.oauth2 as oauth2
import random
import os
import json

#Get Credentials
spotify_client_id = 'b1f3e3b57dff450bbdb7ea0c8d4c6926'
spotify_client_secret = 'b6861efbfb1945dfb4b6a8bc3cd93490'
spotify_redirect_uri = 'http://localhost:8080/main'
spotify_scope = """
playlist-modify-private playlist-modify-public playlist-read-collaborative
playlist-read-private user-read-birthdate
user-read-email user-read-private user-top-read
"""

path_to_token = 'spotify_token.json'
recommendations_playlist_id = '7z8DEEe65seFb4rm0Jd8SE'

print ("Connecting to Spotify")
auth = oauth2.SpotifyOAuth(
	client_id=spotify_client_id,
    client_secret=spotify_client_secret,
    redirect_uri=spotify_redirect_uri,
    cache_path=path_to_token,
    scope=spotify_scope
    )

token_info = auth.get_cached_token()

access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)
user_id = sp.current_user()['id']

#Get top 50 tracks and select random 5
print ("Getting top tracks")
top_tracks_json = sp.current_user_top_tracks(limit=50, time_range='medium_term')
all_top_tracks = [track['id'] for track in top_tracks_json['items']]
top_5_tracks = random.sample(all_top_tracks,5)

#Get recommendations based on top tracks
print ("Getting recommendations")
recommended_tracks_json = sp.recommendations(seed_tracks=top_5_tracks)
recommended_track_ids = [track['id'] for track in recommended_tracks_json['tracks']]

#Replace tracks in Suggestions playlist with the new recommendations
print ("Replacing tracks")
sp.user_playlist_replace_tracks(user_id,recommendations_playlist_id,recommended_track_ids)
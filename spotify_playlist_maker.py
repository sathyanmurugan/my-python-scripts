from spotify.spotify import MySpotify
import spotipy.oauth2 as oauth2
from utilities.utilities import get_credentials
import sys

c = get_credentials()

auth = oauth2.SpotifyOAuth(
	client_id=c.spotify_client_id,
    client_secret=c.spotify_client_secret,
    redirect_uri=c.spotify_redirect_uri,
    cache_path=c.spotify_token,
    scope=c.spotify_scope
    )

token_info = auth.get_cached_token()
token = token_info['access_token']

sp = MySpotify(token)

#Get user data
user_deets = sp.get_user_details()
locale = user_deets['user_locale']
user_id = user_deets['user_id']

#Check if Seed playlist exists
user_playlists = sp.get_user_playlist_ids()

if c.spotify_seed_id not in user_playlists or c.spotify_suggestion_id not in user_playlists:
	print('Seed/Sugg. playlist does not exist, or hasn tbeen updated in parameters. Exiting')
	sys.exit(0)

#Get Tracks from Seed Playlist, Get recommendations based on seed
seed_track_ids = sp.get_track_ids_from_playlist(user_id,c.spotify_seed_id)
recommended_track_ids = sp.get_recommendations(seed_track_ids[:5],locale) #Only 5 tracks allowed as input

#Replace tracks in Suggestions playlist with the new recommendations
sp.replace_tracks_in_playlist(user_id,c.spotify_suggestion_id,recommended_track_ids)

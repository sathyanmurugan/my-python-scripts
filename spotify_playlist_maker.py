from spotify.spotify import MySpotify
import spotipy.oauth2 as oauth2
from utilities.utilities import get_credentials


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

import spotipy
import spotipy.oauth2 as oauth2


auth = oauth2.SpotifyOAuth(
	client_id=c.spotify_client_id,
    client_secret=c.spotify_client_secret,
    redirect_uri=c.spotify_redirect_uri,
    scope=c.spotify_scope
    )

auth.get_authorize_url()
#Copy output from above and get the url it redirects to
url ="""

"""

code = auth.parse_response_code(url)
token_info = auth.get_access_token(code)

#Store token info somewhere

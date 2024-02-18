# Import necessary libraries
from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Spotify OAuth settings
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID', '')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET', '')
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'playlist-read-private'

# Create Spotify OAuth object
def create_spotify_oauth():
    return SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SCOPE)

@app.route('/')
def index():
    # Check if the user is already logged in
    if 'token_info' in session:
        return redirect(url_for('playlists'))
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Spotify callback route
    sp_oauth = create_spotify_oauth()
    session['token_info'] = sp_oauth.get_access_token(request.args.get('code'))
    return redirect(url_for('playlists'))

@app.route('/playlists')
def playlists():
    # Display user's playlists
    sp = spotipy.Spotify(auth_manager=create_spotify_oauth())
    playlists = sp.current_user_playlists()
    return render_template('playlists.html', playlists=playlists['items'])

@app.route('/duplicates/<playlist_id>')
def duplicates(playlist_id):
    sp = spotipy.Spotify(auth_manager=create_spotify_oauth())
    tracks = fetch_all_tracks_from_playlist(sp, playlist_id)
    duplicates, potential_duplicates, missing_info_tracks = find_duplicates(tracks)
    return render_template('duplicates.html', duplicates=duplicates, potential_duplicates=potential_duplicates, missing_info_tracks=missing_info_tracks)


def fetch_all_tracks_from_playlist(sp, playlist_id):
    # Fetch all tracks from the selected playlist
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def find_duplicates(tracks):
    seen_tracks = {}
    duplicates = []
    potential_duplicates = []
    missing_info_tracks = []

    for item in tracks:
        track = item['track']
        if not track or 'id' not in track or not track['name'] or not track['artists']:
            missing_info_tracks.append(track['id'] if track else 'Unknown ID')
            continue
        
        track_id = track['id']
        track_name = track['name']
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        track_duration_ms = track['duration_ms']
        simple_identifier = f"{track_name} - {artist_names}"

        # Check if we have seen this track (excluding duration)
        if simple_identifier in seen_tracks:
            # Now check the duration to decide if it's a potential duplicate
            original_duration = seen_tracks[simple_identifier]['duration']
            duration_difference = abs(original_duration - track_duration_ms)

            # If duration differs by more than 1 second, consider it a potential duplicate
            if duration_difference > 1000:  # More than 1 second
                potential_duplicates.append(f"{simple_identifier} (Duration difference: {duration_difference}ms)")
            else:
                # If duration difference is less than or equal to 1 second, consider it a duplicate
                duplicates.append(simple_identifier)
        else:
            # If we haven't seen this track, add it to seen_tracks
            seen_tracks[simple_identifier] = {'id': track_id, 'duration': track_duration_ms}

    return duplicates, potential_duplicates, missing_info_tracks




if __name__ == '__main__':
    app.run(debug=True, port=5000)

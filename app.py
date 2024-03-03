# Import necessary libraries
from flask import Flask, Response, request, redirect, session, url_for, render_template, flash, jsonify
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
SCOPE = 'playlist-read-private playlist-modify-private playlist-modify-public'

# Create Spotify OAuth object
def get_spotify_oauth():
    return SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SCOPE)

def get_spotify_client():
    sp_oauth = get_spotify_oauth()
    token_info = session.get('token_info', None)

    # Check if the token is available and not expired; refresh if necessary
    if not token_info or sp_oauth.is_token_expired(token_info):
        # Attempt to refresh the token if possible
        if 'refresh_token' in token_info:
            new_token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = new_token_info
            return spotipy.Spotify(auth=new_token_info['access_token'])
        else:
            # Redirect to login if we cannot refresh the token
            flash("Please log in to access your Spotify playlists.", "info")
            return redirect(url_for('login'))
    else:
        # Return a Spotify client if the token is valid
        return spotipy.Spotify(auth=token_info['access_token'])


@app.route('/')
def index():
    # Check if the user is already logged in
    if 'token_info' in session:
        return redirect(url_for('playlists'))
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash("Authorization failed. Please try again.", "error")
        return redirect(url_for('index'))
    
    try:
        # Exchange code for access token, refresh token, and expiration time
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        if not token_info:
            flash("Could not obtain access token. Please try again.", "error")
            return redirect(url_for('index'))
        
        # Store token_info in session for future use
        session['token_info'] = token_info
        return redirect(url_for('playlists'))
    except spotipy.oauth2.SpotifyOauthError as e:
        flash(f"Error obtaining access token: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/privacy')
def privacy():
    return render_template('privacypolicy.html')

@app.route('/terms')
def terms():
    return render_template('termsofservice.html')


@app.route('/playlists')
def playlists():
    sp = get_spotify_client()
    if not sp:
        flash("Session expired. Please log in again.", "warning")
        return render_template('index.html')
    
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        # Assuming the first image is the one you want to use
        playlist['image_url'] = playlist['images'][0]['url'] if playlist['images'] else None
    return render_template('playlists.html', playlists=playlists['items'])



@app.route('/duplicates/<playlist_id>')
def duplicates(playlist_id):
    sp_client = get_spotify_client()
    if isinstance(sp_client, Response):  # If get_spotify_client returned a redirect response
        return sp_client  # Perform the redirect

    # Now sp_client is a valid Spotify client instance
    try:
        tracks = fetch_all_tracks_from_playlist(sp_client, playlist_id)
        duplicates, potential_duplicates, missing_info_tracks = find_duplicates(tracks)
        return render_template('duplicates.html', duplicates=duplicates, potential_duplicates=potential_duplicates, missing_info_tracks=missing_info_tracks, playlist_id=playlist_id)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('playlists'))


def fetch_all_tracks_from_playlist(sp, playlist_id):
    # Fetch all tracks from the selected playlist
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def milliseconds_to_minutes_seconds(ms):
    minutes = ms // 60000
    seconds = ((ms % 60000) + 500) // 1000  # Round to nearest second
    return f"{minutes}:{seconds:02d}"

def find_duplicates(tracks):
    seen_tracks = {}
    duplicates = []
    potential_duplicates = []
    missing_info_tracks = []

    for item in tracks:
        track = item['track']
        if not track or 'id' not in track or not track['name'] or not track['artists']:
            missing_info_tracks.append({'id': track['id'] if track else 'Unknown ID', 'image_url': None})
            continue
        
        track_id = track['id']
        track_name = track['name']
        artist_names = ', '.join([artist['name'] for artist in track['artists']])
        track_duration_ms = track['duration_ms']
        image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        simple_identifier = f"{track_name} - {artist_names}"

        # Check if we have seen this track (excluding duration)
        if simple_identifier in seen_tracks:
            # Now check the duration to decide if it's a potential duplicate
            original_duration = seen_tracks[simple_identifier]['duration']
            duration_difference = abs(original_duration - track_duration_ms)

            # If duration differs by more than 1 second, consider it a potential duplicate
            if duration_difference > 1000:  # More than 1 second
                potential_duplicates.append({
                    'name': simple_identifier, 
                    'track1_id': seen_tracks[simple_identifier]['id'], 
                    'track2_id': track_id,
                    'track1_duration': milliseconds_to_minutes_seconds(seen_tracks[simple_identifier]['duration']),
                    'track2_duration': milliseconds_to_minutes_seconds(track_duration_ms),
                    'duration_difference': milliseconds_to_minutes_seconds(duration_difference),
                    'image_url': image_url
                })
            else:
                # If duration difference is less than or equal to 1 second, consider it a duplicate
                 duplicates.append({'name': simple_identifier, 'id': track_id, 'image_url': image_url})
        else:
            # If we haven't seen this track, add it to seen_tracks
            seen_tracks[simple_identifier] = {'id': track_id, 'duration': track_duration_ms, 'image_url': image_url}
    return duplicates, potential_duplicates, missing_info_tracks

@app.route('/remove_duplicate/<playlist_id>/<track_id>')
def remove_duplicate(playlist_id, track_id):
    if 'token_info' not in session:
        # User is not logged in or session expired
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    user = sp.current_user()
    playlist = sp.playlist(playlist_id)

    # Check if current user is the owner of the playlist
    if playlist['owner']['id'] != user['id']:
        response = {"status": "error", "message": "You do not have permission to modify this playlist."}
        return jsonify(response), 403
    try:
        # Fetch all tracks from the playlist to find the position of the duplicate track
        tracks = fetch_all_tracks_from_playlist(sp, playlist_id)
        occurrences = []
        for i, item in enumerate(tracks):
            if item['track']['id'] == track_id:
                occurrences.append({'uri': item['track']['uri'], 'positions': [i]})

        # If there are multiple occurrences, remove only the first one
        if occurrences:
            sp.playlist_remove_specific_occurrences_of_items(playlist_id, occurrences[:1])
            response = {"status": "success", "message": "Duplicate song removed successfully."}
            return jsonify(response)  # Success response
        else:
            response = {"status": "error", "message": "Track not found."}
            return jsonify(response), 404
    except Exception as e:
        response = {"status": "error", "message": f"Failed to remove track. Error: {str(e)}"}
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

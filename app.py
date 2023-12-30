import threading
import time
import uuid
from flask import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from collections import Counter
import os
import json
import atexit 
from torchAudio import generate_audio

app = Flask(__name__)

genres = []

app.secret_key = os.urandom(24)


@app.route("/")
def index():
    print(session.get('token_info', None))
    token_info = session.get('token_info', None)

    if not token_info:
        sp_oauth = SpotifyOAuth(client_id='68e8cbf419b74c87a3b186176481cf5a',
                                client_secret='87da937ededc445dbbba7efb3eb8facd',
                                redirect_uri='http://127.0.0.1:5000/callback',
                                scope="user-library-read",
                                cache_handler=CacheFileHandler(cache_path=None))
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    else:
        scope = "user-library-read"

        auth_manager = SpotifyOAuth(client_id='68e8cbf419b74c87a3b186176481cf5a',
                                                        client_secret='87da937ededc445dbbba7efb3eb8facd',
                                                        redirect_uri='http://127.0.0.1:5000/callback',
                                                        scope=scope,
                                                        cache_handler=CacheFileHandler(cache_path=None))
        

        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        results = sp.current_user_top_artists(40, 0, 'long_term')

        # Create a list to store the track information
        track_info = []
        # Create a list to store all genres
        all_genres = []

        for idx, item in enumerate(results['items']):
            artist = item['name']
            genres = item['genres']
            image = item['images'][0]['url']
            artistID = item['id']

            # Add genres to the all_genres list
            all_genres.extend(genres)

            track_info.append({
                'index': idx + 1,
                'name': artist,
                'genres': genres,
                'image': image,
                'id': artistID
            })

        # Count the occurrences of each genre
        genre_counts = Counter(all_genres)

        # Sort genres by count in descending order and convert to list
        sorted_genres = [genre for genre, count in genre_counts.most_common()]

        topGenres = sorted_genres[:5]

        with open('top_genres.json', 'w') as f:
            json.dump(topGenres, f)

        # Render a template with the track information
        return render_template("index.html", track_info=track_info, topGenres=topGenres, images=image)

@app.route('/login')
def login():
    # Create an instance of SpotifyOAuth
    sp_oauth = SpotifyOAuth(client_id='68e8cbf419b74c87a3b186176481cf5a',
                            client_secret='87da937ededc445dbbba7efb3eb8facd',
                            redirect_uri='http://127.0.0.1:5000/callback',
                            scope="user-library-read")

    # Redirect the user to the Spotify Accounts service for them to log in
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()

    # Redirect the user to the home page
    return redirect('/')

@app.route('/callback')
def callback():
    # Get the authorization code from the request parameters
    code = request.args.get('code')

    # Create an instance of SpotifyOAuth
    sp_oauth = SpotifyOAuth(client_id='68e8cbf419b74c87a3b186176481cf5a',
                            client_secret='87da937ededc445dbbba7efb3eb8facd',
                            redirect_uri='http://127.0.0.1:5000/callback',
                            scope="user-library-read")

    # Get the access token
    token_info = sp_oauth.get_access_token(code)

    # Save the access token in the session
    session['token_info'] = token_info

    # Redirect the user to the home page
    return redirect('/')

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/process_tracks', methods=['POST'])
def process_tracks():
    global genres
    genres = request.get_json()
    return render_template('loading.html')
tasks = {}

@app.route('/generate_audio')
def generate_audio_route():
    global genres
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    thread = threading.Thread(target=generate_audio, args=(genres,))
    thread.start()
    tasks[task_id] = thread  # Store the thread
    return render_template('loading.html', task_id=task_id)  # Pass the task ID to the template

@app.route('/check_status/<task_id>')
def check_status(task_id):
    thread = tasks.get(task_id)
    if thread is None:
        return jsonify({'status': 'invalid task id'})
    elif thread.is_alive():
        return jsonify({'status': 'not done'})
    else:
        audio_url = thread.join()  # Get the result of the thread
        return jsonify({'status': 'done', 'audio_url': audio_url})


if __name__ == "__main__":
    app.run(debug=True)

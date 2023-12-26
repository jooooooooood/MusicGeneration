import threading
import time
import uuid
from flask import Flask, jsonify, render_template, send_from_directory
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import os
import json
from torchAudio import generate_audio

app = Flask(__name__)
@app.route("/")
def index():

    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='68e8cbf419b74c87a3b186176481cf5a',
                                                    client_secret='81368f1ba3044ed38e4f6616fe4253b8',
                                                    redirect_uri='http://127.0.0.1:5000',
                                                    scope=scope))

    results = sp.current_user_top_artists(40, 0, 'long_term')

    # Create a list to store the track information
    track_info = []
    # Create a list to store all genres
    all_genres = []

    for idx, item in enumerate(results['items']):
        artist = item['name']
        genres = item['genres']

        # Add genres to the all_genres list
        all_genres.extend(genres)

        track_info.append({
            'index': idx + 1,
            'name': artist,
            'genres': genres
        })

    # Count the occurrences of each genre
    genre_counts = Counter(all_genres)

    # Sort genres by count in descending order and convert to list
    sorted_genres = [genre for genre, count in genre_counts.most_common()]

    topGenres = sorted_genres[:5]

    with open('top_genres.json', 'w') as f:
        json.dump(topGenres, f)

    # Render a template with the track information
    return render_template("index.html", track_info=track_info, topGenres=topGenres)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)


tasks = {}

@app.route('/generate_audio')
def generate_audio_route():
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    thread = threading.Thread(target=generate_audio)
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

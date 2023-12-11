import time
import json
from collections import Counter
from flask import flash, redirect, render_template, url_for, session
from models import Journal
def get_daily_theme_genres(journal_id, db):
    try:
        journal = db.session.query(Journal).filter_by(id=journal_id).first()

        if journal:
            daily_themes = journal.daily_themes
            all_genres = [genre.genre_name for theme in daily_themes for genre in theme.genres]

            genre_counts = Counter(all_genres)

            top_genres = [genre for genre, count in genre_counts.most_common(5)]

            return top_genres
        else:
            return None
    except Exception as e:
        flash(f"Error in get_daily_theme_genres: {str(e)}", 'error')
        return None

def get_spotify_recommendations(genres, user, oauth, db, limit=3):
    endpoint = 'recommendations'

    if 'spotify_token' in session:
        token = session['spotify_token']

        if is_token_expired(token):
            flash('Spotify token is expired.', 'error')
            session.pop('spotify_token', None)
            return None
    else:
        flash('Spotify token not found in the session.', 'error')
        return None

    seed_genres = ','.join(genres)

    params = {
        'limit': limit,
        'seed_genres': seed_genres,
    }
    response = oauth.spotify.get(endpoint, params=params, token=token).text
    data = json.loads(response)
    if 'error' in data:
        print(f"Error: {data['error']['status']}, {data['error']['message']}")
        return None
    elif 'tracks' not in data or not data['tracks']:
        print("No recommendations found.")
        return None
    else:
        return data['tracks']

def save_to_saved_tracks(track_uris, oauth, user, db):
    endpoint = 'me/tracks'

    if 'spotify_token' in session:
        token = session['spotify_token']

        if is_token_expired(token):
            flash('Spotify token is expired.', 'error')
            session.pop('spotify_token', None)
            return None
    else:
        flash('Spotify token not found in the session.', 'error')
        return None

    data = {'ids': track_uris}
    response = oauth.spotify.put(endpoint, token=token, params=data).text
    if response:
        response = json.loads(response)

    if 'error' in response:
        error_message = f"Error saving tracks to Saved Tracks: {response['error']['status']}, {response['error']['message']}"
        return False, error_message
    else:
        return True, None

def get_saved_tracks(oauth, user, db, limit=20, offset=0):
    endpoint = 'me/tracks'

    if 'spotify_token' in session:
        token = session['spotify_token']

        if is_token_expired(token):
            flash('Spotify token is expired.', 'error')
            session.pop('spotify_token', None)
            return None
    else:
        flash('Spotify token not found in the session.', 'error')
        return None

    params = {
        'limit': limit,
        'offset': offset
    }

    response = oauth.spotify.get(endpoint, params=params, token=token).text
    data = json.loads(response)

    if 'error' in data:
        print(f"Error: {data['error']['status']}, {data['error']['message']}")
        return None
    else:
        return data

def is_token_expired(token):
    expiration_time = token.get('expires_at', 0)
    return expiration_time < time.time()
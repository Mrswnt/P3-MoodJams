import json
from flask import Flask, render_template, redirect, request, session, url_for, flash
from authlib.integrations.flask_client import OAuth
from models import db, User, Journal, DailyTheme, Genre, journal_dailytheme, dailytheme_genre
from datetime import date, datetime
from dummy_data import create_dummy_data
from keys import secret_key, spotify_client_id, spotify_client_secret
from functions import get_daily_theme_genres, get_spotify_recommendations, save_to_saved_tracks, get_saved_tracks

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moodjams.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

app.config['SPOTIFY_CLIENT_ID'] = spotify_client_id
app.config['SPOTIFY_CLIENT_SECRET'] = spotify_client_secret
app.config['SPOTIFY_REDIRECT_URI'] = 'http://127.0.0.1:5000/spotify-authorize'

oauth = OAuth(app)
oauth.register(
    name="spotify",
    client_id=spotify_client_id,
    client_secret=spotify_client_secret,
    authorize_url="https://accounts.spotify.com/authorize",
    access_token_url="https://accounts.spotify.com/api/token",
    api_base_url="https://api.spotify.com/v1/",
    client_kwargs={
        'scope': 'playlist-read-private playlist-modify-private user-library-modify user-library-read user-read-private'
    }
)

db.init_app(app)

@app.template_filter('format_date')
def format_date(value, format='%d %B %Y'):
    if isinstance(value, date):
        value = datetime.combine(value, datetime.min.time())
    return value.strftime(format)

@app.route('/')
def home():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            return redirect(url_for('journal_list'))
        else:
            return redirect(url_for('login_spotify'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.scalars(db.select(User).filter_by(email=email, password=password).limit(1)).first()

        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('/pages/auth/login.html')

@app.route('/login_spotify')
def login_spotify():
    redirect_uri = url_for('spotify_authorize', _external=True)
    session.pop('spotify_token', None)
    return oauth.spotify.authorize_redirect(redirect_uri)

@app.route('/spotify-authorize')
def spotify_authorize():
    token = oauth.spotify.authorize_access_token()

    if token:
        spotify_user = oauth.spotify.get("me", token=token).text
        spotify_user = json.loads(spotify_user)

        user = db.session.get(User, session['user_id'])
        user.spotify_refresh_token = token["refresh_token"]
        user.spotify_user_id = spotify_user["id"]
        db.session.commit()
        session['spotify_token'] = token

        flash('Spotify authorization successful!', 'success')

    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = db.session.scalars(db.select(User).filter_by(email=email).limit(1)).first()
        if existing_user:
            flash('Email already exists. Please choose a different email.', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('home'))

    return render_template('/pages/auth/register.html')

@app.route('/journal')
def journal_list():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            journals = Journal.query.filter_by(user_id=user.id).order_by(Journal.date.desc()).all()
            return render_template('/pages/journal/list.html', user=user, journal_list=journals)
        else:
            return redirect(url_for('login_spotify'))

    else:
        return redirect(url_for('login'))

@app.route('/journal/add', methods=['GET', 'POST'])
def add_journal():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if 'spotify_token' in session:
            if request.method == 'POST':
                mood_rating = int(request.form.get('moodRating'))
                description = request.form.get('journalDescription')
                selected_daily_themes = request.form.getlist('dailyTheme[]')

                if not (1 <= mood_rating <= 5):
                    flash('Invalid mood rating. Please select a rating between 1 and 5.', 'error')
                elif not description:
                    flash('Description cannot be empty.', 'error')
                elif not selected_daily_themes:
                    flash('Please select at least one daily theme.', 'error')
                else:
                    new_journal = Journal(
                        user_id=user.id,
                        mood_rating=mood_rating,
                        description=description,
                        date=datetime.now()
                    )

                    for theme_id in selected_daily_themes:
                        daily_theme = db.session.get(DailyTheme, theme_id)
                        if daily_theme:
                            new_journal.daily_themes.append(daily_theme)

                    db.session.add(new_journal)
                    db.session.commit()

                    flash('Journal entry added successfully!', 'success')
                    return redirect(url_for('journal_list'))

            daily_themes = db.session.scalars(db.select(DailyTheme)).all()
            return render_template('/pages/journal/add.html', daily_themes=daily_themes)
        else:
            return redirect(url_for('login_spotify'))
    else:
        return redirect(url_for('login'))

@app.route('/journal/details/<int:journal_id>')
def journal_details(journal_id):
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            journal = db.session.get(Journal, journal_id)

            if journal:
                daily_theme_genres = get_daily_theme_genres(journal_id, db)
                if daily_theme_genres:
                    recommendations = get_spotify_recommendations(daily_theme_genres, user, oauth, db, 3)
                    if recommendations:
                        return render_template('/pages/journal/show.html', journal=journal,
                                               recommendations=recommendations)
                    else:
                        flash('No song recommendations found for this journal.', 'error')
                        return render_template('/pages/journal/show.html', journal=journal)
                else:
                    flash('No daily theme genres found for this journal.', 'error')
                    return render_template('/pages/journal/show.html', journal=journal)
            else:
                flash('Journal not found.', 'error')
                return redirect(url_for('journal_list'))
        else:
            return redirect(url_for('login_spotify'))
    else:
        return redirect(url_for('login'))

@app.route('/journal/delete/<int:journal_id>', methods=['POST'])
def delete_journal(journal_id):
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            journal = db.session.get(Journal, journal_id)

            if journal:
                db.session.delete(journal)
                db.session.commit()
                flash('Journal entry deleted successfully!', 'success')
            else:
                flash('Journal entry not found.', 'error')
        else:
            flash('Spotify authorization required to delete journal entries.', 'error')

    return redirect(url_for('journal_list'))

@app.route('/save_track/<string:journal_id>', methods=['POST'])
def save_track(journal_id):
    track_uri = request.form.get('track_uri')
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            success, error_message = save_to_saved_tracks(track_uri, oauth, user, db)
            if success:
                flash('Track saved to Saved Tracks!', 'success')
            else:
                flash(f'Failed to save track to Saved Tracks. {error_message}', 'error')
        else:
            flash('Spotify authorization required to save tracks.', 'error')

    return redirect(url_for('journal_details', journal_id=journal_id))

@app.route('/track')
def saved_tracks_list():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])

        if 'spotify_token' in session:
            limit = 20
            offset = int(request.args.get('offset', 0))

            saved_tracks_data = get_saved_tracks(oauth, user, db, limit=limit, offset=offset)
            if saved_tracks_data:
                total_tracks = saved_tracks_data.get('total', 0)
                items = saved_tracks_data.get('items', [])

                return render_template('/pages/track/list.html', user=user, total_tracks=total_tracks, items=items,
                                       limit=limit, offset=offset)
            else:
                flash('Failed to retrieve saved tracks.', 'error')
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login_spotify'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('spotify_token', None)
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_dummy_data()

    app.run(debug=True)
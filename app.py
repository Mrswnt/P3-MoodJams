import json
from flask import Flask, render_template, redirect, request, session, url_for, flash
from authlib.integrations.flask_client import OAuth
from models import db, User, Journal, DailyTheme, Genre, journal_dailytheme, dailytheme_genre
from datetime import date, datetime
from dummy_data import create_dummy_data
from keys import secret_key, spotify_client_id, spotify_client_secret

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

        if user.spotify_access_token and user.spotify_refresh_token:
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
        user.spotify_access_token = token["access_token"]
        user.spotify_refresh_token = token["refresh_token"]
        user.spotify_user_id = spotify_user["id"]
        db.session.commit()

        session['spotify_token'] = token
        flash('Spotify authorization successful!', 'success')

    return redirect(url_for('home'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        session.pop('spotify_token', None)
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

        if user.spotify_access_token and user.spotify_refresh_token:
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
        if user.spotify_access_token and user.spotify_refresh_token:
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

        if user.spotify_access_token and user.spotify_refresh_token:
            journal = db.session.get(Journal, journal_id)

            if journal:
                return render_template('/pages/journal/show.html', journal=journal)
            else:
                flash('Journal not found.', 'error')
                return redirect(url_for('journal_list'))
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
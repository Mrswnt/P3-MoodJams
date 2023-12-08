from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    spotify_user_id = db.Column(db.String(255), unique=True, nullable=True)
    spotify_access_token = db.Column(db.String(255), nullable=True)
    spotify_refresh_token = db.Column(db.String(255), nullable=True)

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    mood_rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    daily_themes = db.relationship('DailyTheme', secondary='journal_dailytheme', backref='related_journals')

class DailyTheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme_name = db.Column(db.String(255), unique=True, nullable=False)

    journals = db.relationship('Journal', secondary='journal_dailytheme', backref='related_themes')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(255), unique=True, nullable=False)

    daily_themes = db.relationship('DailyTheme', secondary='dailytheme_genre', backref='genres')

journal_dailytheme = db.Table('journal_dailytheme',
    db.Column('journal_id', db.Integer, db.ForeignKey('journal.id'), primary_key=True),
    db.Column('dailytheme_id', db.Integer, db.ForeignKey('daily_theme.id'), primary_key=True)
)

dailytheme_genre = db.Table('dailytheme_genre',
    db.Column('dailytheme_id', db.Integer, db.ForeignKey('daily_theme.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)
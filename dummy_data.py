from datetime import datetime
from models import db, User, Journal, DailyTheme, Genre, journal_dailytheme, dailytheme_genre

mock_user_data = {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'}
mock_user = User(**mock_user_data)

mock_journal_list_data = [
    {'date': '2023-01-15', 'mood_rating': 3, 'themes': ['Family Time', 'Nature'],
     'description': 'Quality time with family in nature.'},
    {'date': '2023-01-20', 'mood_rating': 4, 'themes': ['Me Time', 'Reading'],
     'description': 'Enjoyed a good book during some me time.'},
    {'date': '2023-01-25', 'mood_rating': 5, 'themes': ['Friendship', 'Happy Hour'],
     'description': 'Fun night out with friends at a happy hour.'},
    {'date': '2023-01-30', 'mood_rating': 2, 'themes': ['Love', 'Romantic Dinner'],
     'description': 'Romantic dinner with a loved one.'},
    {'date': '2023-02-05', 'mood_rating': 4, 'themes': ['Adventure', 'Traveling'],
     'description': 'Exciting adventures while traveling.'},
    {'date': '2023-02-10', 'mood_rating': 3, 'themes': ['Coding/Programming', 'Creativity'],
     'description': 'Productive day filled with coding and creativity.'},
    {'date': '2023-02-15', 'mood_rating': 5, 'themes': ['Gaming', 'Excited'],
     'description': 'High-energy gaming session.'},
    {'date': '2023-02-20', 'mood_rating': 1, 'themes': ['Meditation', 'Stressed'],
     'description': 'Attempted meditation to cope with stress.'},
    {'date': '2023-02-25', 'mood_rating': 4, 'themes': ['Creativity', 'Happy'],
     'description': 'Expressed creativity and felt happy about the outcome.'},
    {'date': '2023-03-01', 'mood_rating': 3, 'themes': ['Happy Hour', 'Dancing'],
     'description': 'Danced the night away at a happy hour event.'},
    {'date': '2023-03-05', 'mood_rating': 2, 'themes': ['Rainy Day', 'Reflective'],
     'description': 'Reflective moments on a cozy rainy day.'},
    {'date': '2023-03-10', 'mood_rating': 4, 'themes': ['Productivity', 'Workout'],
     'description': 'Achieved high productivity and a good workout.'},
    {'date': '2023-03-15', 'mood_rating': 5, 'themes': ['Dancing', 'Excited'],
     'description': 'Spontaneous dancing and excitement.'},
]

mock_recommendations_data = [
    {'name': 'Blinding Lights', 'artist': 'The Weeknd',
     'cover': 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36',
     'spotify_link': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b'},
    {'name': 'Someone You Loved', 'artist': 'Lewis Capaldi',
     'cover': 'https://i.scdn.co/image/ab67616d00001e02fc2101e6889d6ce9025f85f2',
     'spotify_link': 'https://open.spotify.com/track/7qEHsqek33rTcFNT9PFqLf'},
    {'name': 'Watermelon Sugar', 'artist': 'Harry Styles',
     'cover': 'https://i.scdn.co/image/ab67616d00001e0277fdcfda6535601aff081b6a',
     'spotify_link': 'https://open.spotify.com/track/6UelLqGlWMcVH1E5c4H7lY'}
]

daily_themes_data = {
    "Family Time": ["acoustic", "folk", "country", "singer-songwriter"],
    "Me Time": ["ambient", "chill", "classical", "piano", "jazz"],
    "Friendship": ["pop", "indie-pop", "rock", "alternative"],
    "Love": ["pop", "r-n-b", "soul", "singer-songwriter"],
    "Heartbreak": ["sad", "acoustic", "blues", "alternative"],
    "Study": ["ambient", "classical", "instrumental", "piano"],
    "Workout": ["work-out", "edm", "electronic", "pop"],
    "Traveling": ["world-music", "reggae", "latin", "salsa"],
    "Adventure": ["soundtracks", "orchestra", "epic"],
    "Nature": ["ambient", "acoustic", "folk", "new-age"],
    "Romantic Dinner": ["jazz", "blues", "soul", "swing"],
    "Coding/Programming": ["edm", "electronic", "techno", "idm"],
    "Reading": ["classical", "instrumental", "ambient", "piano"],
    "Gaming": ["electronic", "chiptune", "edm", "rock"],
    "Meditation": ["ambient", "new-age", "chill", "instrumental"],
    "Creativity": ["indie", "indie-pop", "folk", "singer-songwriter"],
    "Happy Hour": ["pop", "dance", "upbeat", "funk"],
    "Rainy Day": ["ambient", "chill", "jazz", "acoustic"],
    "Productivity": ["electronic", "edm", "instrumental", "techno"],
    "Dancing": ["dance", "electronic", "pop", "disco"],
}


def create_dummy_data():
    db.create_all()

    if not User.query.filter_by(name='John Doe').first():
        user_data = {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'}
        mock_user = User(**user_data)
        db.session.add(mock_user)

    for theme_name, genres in daily_themes_data.items():
        theme = DailyTheme.query.filter_by(theme_name=theme_name).first()
        if not theme:
            theme = DailyTheme(theme_name=theme_name)
            db.session.add(theme)
            db.session.commit()
            for genre_name in genres:
                genre = Genre.query.filter_by(genre_name=genre_name).first()
                if not genre:
                    genre = Genre(genre_name=genre_name)
                    theme.genres.append(genre)
                    db.session.add(genre)
            db.session.commit()

    db.session.commit()

    if not Journal.query.first():
        daily_themes = DailyTheme.query.all()
        for journal_data in mock_journal_list_data:
            journal = Journal(
                user_id=mock_user.id,
                date=datetime.strptime(journal_data['date'], '%Y-%m-%d'),
                mood_rating=journal_data['mood_rating'],
                description=journal_data['description'],
            )
            for theme_name in journal_data['themes']:
                theme = next((theme for theme in daily_themes if theme.theme_name == theme_name), None)
                if theme:
                    journal.daily_themes.append(theme)
            db.session.add(journal)
    db.session.commit()


if __name__ == "__main__":
    create_dummy_data()
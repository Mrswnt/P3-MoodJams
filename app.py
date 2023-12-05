from flask import Flask, render_template, redirect
from datetime import datetime

app = Flask(__name__, template_folder='templates')

# Dummy Data for Testing the Views
mock_user = {'name': 'John Doe'}
mock_journal_list = [
    {'date': '2023-01-15', 'rating': 3, 'themes': ['Family Time', 'Nature'], 'description': 'Quality time with family in nature.'},
    {'date': '2023-01-20', 'rating': 4, 'themes': ['Me Time', 'Reading'], 'description': 'Enjoyed a good book during some me time.'},
    {'date': '2023-01-25', 'rating': 5, 'themes': ['Friendship', 'Happy Hour'], 'description': 'Fun night out with friends at a happy hour.'},
    {'date': '2023-01-30', 'rating': 2, 'themes': ['Love', 'Romantic Dinner'], 'description': 'Romantic dinner with a loved one.'},
    {'date': '2023-02-05', 'rating': 4, 'themes': ['Adventure', 'Traveling'], 'description': 'Exciting adventures while traveling.'},
    {'date': '2023-02-10', 'rating': 3, 'themes': ['Coding/Programming', 'Creativity'], 'description': 'Productive day filled with coding and creativity.'},
    {'date': '2023-02-15', 'rating': 5, 'themes': ['Gaming', 'Excited'], 'description': 'High-energy gaming session.'},
    {'date': '2023-02-20', 'rating': 1, 'themes': ['Meditation', 'Stressed'], 'description': 'Attempted meditation to cope with stress.'},
    {'date': '2023-02-25', 'rating': 4, 'themes': ['Creativity', 'Happy'], 'description': 'Expressed creativity and felt happy about the outcome.'},
    {'date': '2023-03-01', 'rating': 3, 'themes': ['Happy Hour', 'Dancing'], 'description': 'Danced the night away at a happy hour event.'},
    {'date': '2023-03-05', 'rating': 2, 'themes': ['Rainy Day', 'Reflective'], 'description': 'Reflective moments on a cozy rainy day.'},
    {'date': '2023-03-10', 'rating': 4, 'themes': ['Productivity', 'Workout'], 'description': 'Achieved high productivity and a good workout.'},
    {'date': '2023-03-15', 'rating': 5, 'themes': ['Dancing', 'Excited'], 'description': 'Spontaneous dancing and excitement.'},
]

mock_journal = mock_journal_list[0]
mock_recommendations = [
    {'name': 'Blinding Lights', 'artist': 'The Weeknd', 'cover': 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36', 'spotify_link': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b'},
    {'name': 'Someone You Loved', 'artist': 'Lewis Capaldi', 'cover': 'https://i.scdn.co/image/ab67616d00001e02fc2101e6889d6ce9025f85f2', 'spotify_link': 'https://open.spotify.com/track/7qEHsqek33rTcFNT9PFqLf'},
    {'name': 'Watermelon Sugar', 'artist': 'Harry Styles', 'cover': 'https://i.scdn.co/image/ab67616d00001e0277fdcfda6535601aff081b6a', 'spotify_link': 'https://open.spotify.com/track/6UelLqGlWMcVH1E5c4H7lY'}
]

daily_themes = {
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

@app.template_filter('format_date')
def format_date(value, format='%d %B %Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('/pages/auth/login.html')

@app.route('/register')
def register():
    return render_template('/pages/auth/register.html')

@app.route('/journal')
def journal_list():
    return render_template('/pages/journal/list.html', user=mock_user, journal_list=mock_journal_list)

@app.route('/journal/add')
def add_journal():
    return render_template('/pages/journal/add.html', daily_themes=daily_themes)

@app.route('/journal/details')
def journal_details():
    return render_template('/pages/journal/show.html', journal=mock_journal, recommendations=mock_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
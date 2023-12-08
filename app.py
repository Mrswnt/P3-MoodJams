from flask import Flask, render_template, redirect
from models import db, User, Journal, DailyTheme, Genre, journal_dailytheme, dailytheme_genre
from datetime import datetime
from dummy_data import create_dummy_data

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moodjams.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.template_filter('format_date')
def format_date(value, format='%d %B %Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

@app.route('/')
def home():
    user = User.query.first()
    if user:
        return f"Database is created successfully! User: {user.name}, Email: {user.email}"
    else:
        return "Database is not created or is empty. Please check your database setup."

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
    with app.app_context():
        db.create_all()
        create_dummy_data()

    app.run(debug=True)
from flask import Flask, render_template, redirect, request, session, url_for
from models import db, User, Journal, DailyTheme, Genre, journal_dailytheme, dailytheme_genre
from datetime import datetime
from dummy_data import create_dummy_data
from keys import secret_key

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moodjams.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

db.init_app(app)

@app.template_filter('format_date')
def format_date(value, format='%d %B %Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('journal_list'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "Invalid login credentials. Please try again."

    return render_template('/pages/auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already exists. Please choose a different email."

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(url_for('home'))

    return render_template('/pages/auth/register.html')

@app.route('/journal')
def journal_list():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        journals = Journal.query.filter_by(user_id=user.id).all()
        return render_template('/pages/journal/list.html', user=user, journal_list=journals)
    else:
        return redirect(url_for('login'))

@app.route('/journal/add')
def add_journal():
    return render_template('/pages/journal/add.html', daily_themes=daily_themes)

@app.route('/journal/details')
def journal_details():
    return render_template('/pages/journal/show.html', journal=mock_journal, recommendations=mock_recommendations)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_dummy_data()

    app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from models import create_project, create_user, User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(db, user_id)


# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.get_by_username(db, username)

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        errors = []

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')

        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if User.get_by_username(db, username):
            errors.append('Username already exists.')

        if User.get_by_email(db, email):
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        new_user = create_user(username, email, password)
        db.users.insert_one(new_user)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# --- Protected Routes ---
@app.route('/')
@login_required
def index():
    projects = db.projects.find()
    return render_template('index.html', projects=projects)


@app.route('/item/<id>')
@login_required
def details(id):
    item = db.projects.find_one({"_id": ObjectId(id)})
    return render_template('details.html', item=item)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        repo_name = request.form.get('repo_name')
        repo_url = request.form.get('repo_url')
        language = request.form.get('primary_language')

        new_project = create_project(repo_name, repo_url, language)
        db.projects.insert_one(new_project)

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    item = db.projects.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        name = request.form.get('name')
        db.projects.update_one({"_id": ObjectId(id)}, {"$set": {"name": name}})
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)

@app.route('/delete/<id>', methods=['POST'])
@login_required
def delete(id):
    db.projects.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q')
    if query:
        results = db.projects.find({"name": {"$regex": query, "$options": "i"}})
    else:
        results = []
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
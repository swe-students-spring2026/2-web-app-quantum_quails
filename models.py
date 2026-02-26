# Mongo DB Schema

from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# --- USER CLASS (Flask-Login) ---
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password_hash = user_data["password_hash"]
        self.preferred_languages = user_data.get("preferred_languages", [])
        self.experience_level = user_data.get("experience_level", "beginner")
        self.saved_issues = user_data.get("saved_issues", [])
        self._is_active = user_data.get("is_active", True)

    @property
    def is_active(self):
        return self._is_active

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(db, user_id):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_username(db, username):
        user_data = db.users.find_one({"username": username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_email(db, email):
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User(user_data)
        return None


# --- USER SCHEMA ---
def create_user(username, email, password, languages=None, experience_level=None):
    return {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password, method='pbkdf2:sha256'),
        "preferred_languages": languages or [],
        "experience_level": experience_level or "beginner",
        "saved_issues": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

# --- PROJECT SCHEMA ---
def create_project(repo_name, repo_url, language):
    return {
        "repo_name": repo_name,
        "repo_url": repo_url,
        "primary_language": language
    }

# --- ISSUE SCHEMA ---
def create_issue(project_id, title, issue_url, difficulty_level):
    return {
        "project_id": ObjectId(project_id),
        "title": title,
        "issue_url": issue_url,
        "difficulty_level": difficulty_level,
        "is_active": True,
        "created_at": datetime.now(datetime.timezone.utc)
    }
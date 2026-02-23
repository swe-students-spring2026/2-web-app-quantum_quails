# Mongo DB Schema

from datetime import datetime

# --- USER SCHEMA ---
def create_user(username, email, languages, experience_level):
    return {
        "username": username,
        "email": email,
        "preferred_languages": languages,
        "experience_level": experience_level,
        "saved_issues": [],
        "created_at": datetime.now(datetime.timezone.utc)
    }

# --- PROJECT SCHEMA ---
def create_project(repo_name, repo_url, language):
    return {
        "repo_name": repo_name,
        "repo_url": repo_url,
        "primary_language": language
    }
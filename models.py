# Mongo DB Schema

from datetime import datetime
from bson.objectid import ObjectId

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

# --- ISSUE SCHEMA ---
def create_issue(project_id, title, issue_url, difficulty_level):
    return {
        "project_id": ObjectId(project_id),
        "title": title,
        "issue_url": issue_url,
        "difficulty_label": difficulty_level,
        "is_active": True,
        "created_at": datetime.now(datetime.timezone.utc)
    }
import requests
import base64
import os
import markdown

GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_headers():
    # Return headers with auth token if available
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def extract_owner_repo(repo_url):
    # Extract owner and repo name from a GitHub URL
    try:
        if "github.com/" in repo_url:
            path = repo_url.split("github.com/")[1]
        else:
            path = repo_url
        owner, repo = path.strip("/").split("/")[:2]
        return owner, repo
    except Exception:
        return None


def fetch_readme(owner, repo):
    # Fetch and decode README content for a repository
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"

    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            content_b64 = data.get("content", "")
            if content_b64:
                decoded = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
                html = markdown.markdown(decoded, extensions=['fenced_code', 'tables'])
                return html
        return None
    except Exception:
        return None


def fetch_issues(owner, repo, limit=3):
    # Fetch top open issues for a repository
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": limit}

    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=10)
        if resp.status_code == 200:
            issues_data = resp.json()
            return [
                {"title": issue.get("title", ""), "url": issue.get("html_url", "")}
                for issue in issues_data
            ]
        return []
    except Exception:
        return []


def fetch_languages(owner, repo):
    # Fetch language breakdown for a repository
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"

    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            languages_data = resp.json()
            sorted_langs = sorted(languages_data.items(), key=lambda x: x[1], reverse=True)
            return [lang for lang, _ in sorted_langs]
        return []
    except Exception:
        return []


def detect_tech_stack(languages):
    # Detect likely tech stack based on languages
    tech_stack = []
    lang_lower = [l.lower() for l in languages]

    if "javascript" in lang_lower or "typescript" in lang_lower:
        tech_stack.append("Node.js")
    if "python" in lang_lower:
        tech_stack.append("Flask/Django")
    if "ruby" in lang_lower:
        tech_stack.append("Rails")
    if "java" in lang_lower:
        tech_stack.append("Spring")
    if "go" in lang_lower:
        tech_stack.append("Go")
    if "rust" in lang_lower:
        tech_stack.append("Rust")

    return tech_stack[:3]


def fetch_repo_extended_data(repo_url):
    # Fetch all extended data for a repository.
    result = {
        "readme": None,
        "issues": [],
        "languages": [],
        "tech_stack": []
    }

    owner_repo = extract_owner_repo(repo_url)
    if not owner_repo:
        return result

    owner, repo = owner_repo

    result["readme"] = fetch_readme(owner, repo)
    result["issues"] = fetch_issues(owner, repo)

    all_languages = fetch_languages(owner, repo)
    if len(all_languages) > 1:
        result["languages"] = all_languages[1:5]

    result["tech_stack"] = detect_tech_stack(all_languages)

    return result

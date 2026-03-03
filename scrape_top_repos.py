import requests
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing. Please check your .env file.")

client = MongoClient(MONGO_URI)

db = client.get_default_database(default="github_data")
projects_collection = db["projects"]

def get_top_1000_repos():
    repos_to_insert = []
    
    for page in range(1, 11):
        print(f"Fetching page {page} of 10...")
        
        url = f"https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc&per_page=100&page={page}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get("items", []):
                repo_doc = {
                    "repo_name": item["name"],
                    "repo_url": item["html_url"].replace("https://", ""), 
                    "primary_language": item["language"].lower() if item["language"] else "unknown"
                }
                repos_to_insert.append(repo_doc)
        elif response.status_code == 403:
            print("\nRate limit hit! The unauthenticated search API limit is 10 requests per minute.")
            break
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            break

        time.sleep(5) 

    return repos_to_insert

def main():
    print("Starting GitHub API data retrieval...")
    repos = get_top_1000_repos()
    
    if repos:
        print(f"\nSuccessfully fetched {len(repos)} repositories. Inserting into MongoDB...")
        result = projects_collection.insert_many(repos)
        print(f"Success! Inserted {len(result.inserted_ids)} documents into the '{projects_collection.name}' collection.")
    else:
        print("\nNo repositories were fetched. Check your connection or rate limits.")

if __name__ == "__main__":
    main()
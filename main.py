import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()

def get_repo_owner():
    return os.getenv('GITHUB_REPOSITORY_OWNER')

def get_github_token():
    return os.getenv('INPUT_TOKEN')

def get_output_path():
    return os.environ.get("INPUT_OUTPUT", "languages.json")

def send_api_request(url, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_owner_repositories(owner, token):
    url = f"https://api.github.com/user/repos"
    return send_api_request(url, token)

def get_repository_languages(owner, repo_name, token):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
    return send_api_request(url, token)

def main():
    token = get_github_token()
    owner = get_repo_owner()
    output_path = get_output_path()

    print(f"Owner: {owner}, Token: {'***' if token else 'Not set'}")
    repos = get_owner_repositories(owner, token)
    print(f"Fetched {len(repos)} repositories for owner '{owner}'.")

    # Fetch languages for each repository
    for repo in repos:
        repo_name = repo['name']
        languages = get_repository_languages(owner, repo_name, token)
        print(f"Repository: {repo_name}, Languages: {list(languages.keys())}")
        with open(output_path, 'a') as f:
            json.dump({repo_name: languages}, f)
            f.write('\n')

if __name__ == "__main__":
    main()
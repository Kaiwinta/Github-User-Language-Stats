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
    return os.environ.get("INPUT_OUTPUT", "dist/languages.json")

def get_include_forks():
    return os.environ.get("INPUT_INCLUDE_FORKS", "false").lower() == "true"

def get_owned_only():
    return os.environ.get("INPUT_OWNED_ONLY", "true").lower() == "true"

def get_attribution_mode():
    return os.environ.get("INPUT_ATTRIBUTION_MODE", "raw").lower()

def get_request_timeout():
    try:
        return int(os.environ.get("INPUT_TIMEOUT_SECONDS", "20"))
    except ValueError:
        return 20

def send_api_request(url, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers, timeout=get_request_timeout())
    if response.status_code != 200:
        print(f"API request failed with status code {response.status_code} for URL: {url}")
        return {}
    return response.json()

def get_owner_repositories(owner, token):
    del owner
    repos = []
    page = 1
    affiliation = "owner" if get_owned_only() else "owner,collaborator,organization_member"

    while True:
        url = (
            "https://api.github.com/user/repos"
            f"?per_page=100&page={page}&affiliation={affiliation}&sort=updated"
        )
        page_data = send_api_request(url, token)
        if not isinstance(page_data, list) or not page_data:
            break

        repos.extend(page_data)
        if len(page_data) < 100:
            break
        page += 1

    return repos

def get_repository_languages(languages_url, token):
    url = languages_url
    return send_api_request(url, token)

def get_commit_ratio_for_owner(repo_full_name, owner_login, token):
    url = f"https://api.github.com/repos/{repo_full_name}/contributors"
    contributors = send_api_request(url, token)

    if not isinstance(contributors, list):
        return None

    total_commits = 0
    owner_commits = 0
    for contributor in contributors:
        commits = contributor.get("contributions", 0)
        total_commits += commits
        if (contributor.get("login") or "").lower() == owner_login.lower():
            owner_commits += commits

    if total_commits == 0:
        return None

    return owner_commits / total_commits

def main():
    token = get_github_token()
    owner = get_repo_owner()
    output_path = get_output_path()
    include_forks = get_include_forks()
    attribution_mode = get_attribution_mode()

    print(f"owned_only={get_owned_only()}, include_forks={include_forks}, attribution_mode={attribution_mode}")

    if not owner:
        raise ValueError("GITHUB_REPOSITORY_OWNER is not set")
    if not token:
        raise ValueError("INPUT_TOKEN is not set")
    if attribution_mode not in {"raw", "commit_ratio"}:
        raise ValueError("INPUT_ATTRIBUTION_MODE must be 'raw' or 'commit_ratio'")

    repos = get_owner_repositories(owner, token)
    print(f"Fetched {len(repos)} repositories for owner '{owner}'.")

    user_languages = dict()
    for repo in repos:
        if repo.get("fork") and not include_forks:
            continue

        if get_owned_only():
            repo_owner = ((repo.get("owner") or {}).get("login") or "").lower()
            if repo_owner != owner.lower():
                continue

        languages_url = repo.get("languages_url")
        if not languages_url:
            continue

        languages = get_repository_languages(languages_url, token)
        commit_ratio = 1.0
        if attribution_mode == "commit_ratio":
            ratio = get_commit_ratio_for_owner(repo.get("full_name", ""), owner, token)
            if ratio is None:
                ratio = 1.0
            commit_ratio = ratio

        for language in languages.keys():
            weighted = int(round(languages[language] * commit_ratio))
            print(f"Repo: {repo.get('full_name')}, Language: {language}, Bytes: {languages[language]}, Commit Ratio: {commit_ratio:.2f}, Weighted: {weighted}")
            user_languages[language] = user_languages.get(language, 0) + weighted

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({owner: user_languages}, f)
        f.write('\n')

if __name__ == "__main__":
    main()
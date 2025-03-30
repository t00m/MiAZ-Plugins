#!/usr/bin/python3
# File: download_plugin_index.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Retrieve MiAZ plugin index file

import os
import requests
from pprint import pprint

# Read Only token for GitHub repository MiAZ-Plugins
token = "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"


def get_files_from_repo(owner, repo, file_name, branch='main'):
    """Retrieve MiAZ plugin index file

    Args:
        owner: Repository owner
        repo: Repository name
        file_name: The file to look for
        branch: Branch name (default: 'main')
    """
    headers = {'Authorization': f'token {token}'} if token else {}
    base_url = f'https://api.github.com/repos/{owner}/{repo}/contents/'
    params = {'ref': branch}  # This parameter specifies the branch

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        contents = response.json()
        for item in contents:
            if item['name'] == file_name:
                file_url = item['download_url']
                response = requests.get(file_url)
                response.raise_for_status()
                print(f"Downloaded {file_name} from repo {repo} (branch: {branch})")
                return response.json()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    REPO_OWNER = "t00m"
    REPO_NAME = "MiAZ-Plugins"
    TARGET_FILE = "index-plugins.json"
    BRANCH_NAME = "sandbox"  # Specify your branch here
    result = get_files_from_repo(REPO_OWNER, REPO_NAME, TARGET_FILE, BRANCH_NAME)
    assert type(result) == dict



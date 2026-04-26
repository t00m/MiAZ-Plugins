#!/usr/bin/python3
# File: download_plugin_index.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Retrieve MiAZ plugin index file
# Version 0.1

import os
import logging
import requests
from pprint import pprint
from requests.exceptions import HTTPError

log = logging.getLogger(__name__)

REPO_OWNER = "t00m"
REPO_NAME = "MiAZ-Plugins"
TARGET_FILE = "index-plugins.json"
BRANCH_NAME = "sandbox"


def _get_auth_headers():
    token = os.getenv('GITHUB_TOKEN', '')
    return {'Authorization': f'token {token}'} if token else {}


def get_files_from_repo(owner, repo, file_name, branch='main'):
    """Retrieve MiAZ plugin index file

    Args:
        owner: Repository owner
        repo: Repository name
        file_name: The file to look for
        branch: Branch name (default: 'main')
    """
    headers = _get_auth_headers()
    base_url = f'https://api.github.com/repos/{owner}/{repo}/contents/'
    params = {'ref': branch}

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        contents = response.json()
        for item in contents:
            if item['name'] == file_name:
                file_url = item['download_url']
                response = requests.get(file_url)
                response.raise_for_status()
                log.info("Downloaded %s from repo %s (branch: %s)", file_name, repo, branch)
                return response.json()
    except HTTPError as http_err:
        log.error("HTTP error occurred: %s", http_err)
    except Exception as err:
        log.error("An error occurred: %s", err)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = get_files_from_repo(REPO_OWNER, REPO_NAME, TARGET_FILE, BRANCH_NAME)
    assert isinstance(result, dict)

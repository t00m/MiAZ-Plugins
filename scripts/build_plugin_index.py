#!/usr/bin/python3
# File: build_plugin_index.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Scan plugin directory and create the file index-plugins.json
# Version 0.1

import os
import glob
import shutil
import zipfile
import tempfile
from pathlib import Path

def extract_and_find_plugin(zip_path):
    """
    Extracts a zip file to a temporary directory and returns the first .plugin file found.

    Args:
        zip_path (str): Path to the zip file

    Returns:
        Path: Path to the .plugin file
        str: Temporary directory path (for cleanup)

    Raises:
        FileNotFoundError: If no .plugin file is found
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Search for .plugin files
        plugin_files = list(Path(temp_dir).rglob('*.plugin'))

        if not plugin_files:
            raise FileNotFoundError("No .plugin file found in the archive")

        # Return the first .plugin file found and the temp directory
        return plugin_files[0], temp_dir

    except Exception as e:
        # Clean up temp directory if something goes wrong
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


def parse_plugin_file(file_path):
    plugin_dict = {}

    with open(file_path, 'r') as file:
        # Skip the first line (assuming it's [Plugin])
        next(file)

        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Split each line at the first '=' character
            if '=' in line:
                key, value = line.split('=', 1)
                plugin_dict[key.strip()] = value.strip()

    return plugin_dict


plugin_files = glob.glob('plugins/*.zip')

for plugin_file in plugin_files:
    try:
        plugin_path, temp_dir = extract_and_find_plugin(plugin_file)
        plugin_info_path = os.path.join(temp_dir, plugin_path)
        plugin_info = parse_plugin_file(plugin_info_path)
        print(f"{plugin_info['Name']} v{plugin_info['Version']}")
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as error:
        print(f"Error handling plugin {plugin_file}: {error}")

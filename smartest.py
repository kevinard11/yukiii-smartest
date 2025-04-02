from properties import microservices
import yaml
from git import Repo
from pathlib import Path

def run_smartest(repo_url, is_print):
    repo_url_split = repo_url.split("/")
    local_path = f"C://Users//ARD//Desktop//{repo_url_split[-2]}//{repo_url_split[-1]}"

    clone_repo(repo_url, local_path)

    config_path = find_config(local_path)
    mss = ""

    if config_path:
        # config_path = "C://Users//ARD//Desktop//robot-shop//smartest.yaml"

        # Import config
        config = import_config(config_path)

        # Create microservices
        mss = create_microservices(config)

        if is_print:
            print_mss(mss)

    return mss

def create_microservices(config):
    mss = microservices.Microservices(config)
    return mss

def print_mss(mss):
    mss.print()
    for ms in mss.services:
        ms.print()

def import_config(filepath):
    # read yaml configuration
    config = {}
    with open(filepath, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)

    return config

def clone_repo(repo_url, local_path):
    if not path_exist(local_path):
        try:
            print(f"Folder doesn't exist, clone folder")
            Repo.clone_from(repo_url, local_path)
            print(f"Repo cloned to {local_path}")
        except Exception as e:
            print(f"Error cloning repo: {e}")

def path_exist(dir_path):
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        return True
    else:
        return False

def find_config(dir_path):
    target_file = dir_path + "//smartest.yaml"
    search_path = Path(target_file)

    if search_path.exists():
        return str(search_path)
    else:
        return None
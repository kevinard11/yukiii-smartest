from properties import microservices, mongo_db
import yaml, shutil, os, stat
from git import Repo
from pathlib import Path

def run_smartest(repo_url, is_save):
    repo_url_split = repo_url.split("/")
    # local_path = f"C://Users//ARD//Desktop//{repo_url_split[-2]}//{repo_url_split[-1]}"
    local_path = f"./{repo_url_split[-2]}/{repo_url_split[-1]}"

    clone_repo(repo_url, local_path)

    config_path = find_config(local_path)
    smartest_id = ""

    if config_path:

        # Import config
        config = import_config(config_path)
        config['root-dir'] = local_path + '/'

        # Create microservices
        mss = create_microservices(config)

        if is_save:
            # print_mss(mss)
            smartest_id = mongo_db.insert_data_microservices(mss.to_response(), repo_url)
    else:
        return "401"

    return smartest_id

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

# Handler untuk force delete file read-only
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)  # ubah ke writable
    func(path)

def clone_repo(repo_url, local_path):
    if path_exist(local_path):
        # 1. Hapus folder kalau sudah ada
        print(f"Menghapus folder lama: {local_path}")
        shutil.rmtree(local_path, onerror=remove_readonly)

    try:
        print(f"Clone folder")
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
    target_file = dir_path + "/smartest.yaml"
    search_path = Path(target_file)

    if search_path.exists():
        return str(search_path)
    else:
        return None

def find_10_latest_smartest():
    return mongo_db.get_10_latest_data_smartest()

def find_smartest(smartest_id):
    return mongo_db.get_data_smartest_by_id(smartest_id)
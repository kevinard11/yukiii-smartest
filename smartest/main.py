import smartest
import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-r","--repo", help="git url")
    parser.add_argument("--print", help="git url", action="store_true")
    parsed_config = parser.parse_args()

    repo_url = parsed_config.repo
    is_print = parsed_config.print

    smartest.run_smartest(repo_url, is_print)

if __name__ == "__main__":
    main()


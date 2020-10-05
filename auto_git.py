import os
import sys
import json
import time
import asyncio
import requests
from argparse import ArgumentParser
from pathlib import Path
from git import Repo
import git
from pprint import pprint
import subprocess

INTERVAL_SECONDS = 7  # 60 in deployment version

DESCRIPTION = "Track file and automatic push to remote github repository."
EPILOG = "For more information, visit the project page on: https://github.com/yairfine/auto-git"
HELP_FILE_PATH = "the path to the file you want to track."
HELP_FIRST_CONFIG = "configure system and exit"
HELP_NEW_TRACK = "initiate a new tracking configuration for a given file"
HELP_START_TRACK = "start tracking a given file and it's directory"
METAVAR_FILE_PATH = "<file_path>"

ERR_PAT_EXISTS = "It's seems like you already configured this system, try to run again with -n/-s flag"
ERR_CREATE_REMOTE = ' ~~ Error creating remote repo ~~ '
ERR_SETTINGS_LOCAL_EXISTS = "It's seems like you already initiated this directory, try to run again with -s flag"
ERR_PARSE_JSON = " ~~ Error parsing json ~~ "
ERR_STATUS_CODE = "Respone code is not ok - {} - {}"

MSG_END_NEW_TRACK = "Done preparing for a new track"
MSG_START_TRACKING = """Started tracking changes on file '{}'
To stop: press Ctrl+C and wait a few seconds"""
MSG_END_TRACKING = "Tracking session has ended"
MSG_CHANGE_RECORDED = "A change was recorded - {}"
MSG_COMMIT = "commit no.{} - {}"

PROMPT_PAT = """Welcome to auto-git!
Please paste your Private Accesses Token here
Your PAT: """
PROMPT_REPO_NAME = """You've never tracked this directory before.
Please enter a NAME for new remote repository: """

SETTINGS_DIR_GLOBAL = Path.home() / 'auto-git-settings'
SETTINGS_FILE_GLOBAL = SETTINGS_DIR_GLOBAL / 'auto_git_settings_global.txt'

API_BASE_URL = 'https://api.github.com'


def initiate_settings_global():
    """Create 'auto-git-settings' directory in home dir, and a settings file in it.
    """
    try:
        SETTINGS_DIR_GLOBAL.mkdir()
        SETTINGS_FILE_GLOBAL.touch(exist_ok=False)

    except FileExistsError:
        print(ERR_PAT_EXISTS)
        raise


def system_is_configured():
    """Check if the computer that runs the program is already has the global settings file with PAT, user-name, etc

    Returns:
        bool: True if the global settings file is already configured in the compter, False otherwise
    """
    if not SETTINGS_DIR_GLOBAL.is_dir():
        return False
    elif not SETTINGS_FILE_GLOBAL.is_file():
        return False
    elif SETTINGS_FILE_GLOBAL.stat().st_size == 0:
        return False
    else:
        return True


def cleanup_settings_global():
    """remove the 'auto-git-settings' directory and the global-settings-file in it, from home dir (~/).
    """
    SETTINGS_FILE_GLOBAL.unlink()
    SETTINGS_DIR_GLOBAL.rmdir()


def initiate_settings_local_dir(settings_file, readme_file, gitignore_file):
    """Create settings-file and git repo files in the directory

    Args:
        settings_file (Pathlib Path): settings-file to create
        readme_file (Pathlib Path): README.md file to create
        gitignore_file (Pathlib Path): .gitignore file to create
    """
    try:
        settings_file.touch(exist_ok=False)
        readme_file.touch(exist_ok=False)
        gitignore_file.touch(exist_ok=False)

    except FileExistsError:
        print(ERR_SETTINGS_LOCAL_EXISTS)
        sys.exit()


def dir_is_initiated(dir_path):
    """Check if the directory has a settings file, with repo_name, ssh_url, etc.

    Args:
        dir_path (Pathlib Path): The path to the directory

    Returns:
        bool: True if the local settings file is already configured in this directory, False otherwise
    """
    settings_file_local = dir_path / 'auto_git_settings.txt'

    if not settings_file_local.is_file():
        return False
    elif settings_file_local.stat().st_size == 0:
        return False
    else:
        return True


def cleanup_settings_local(dir_path):
    """remove the settings-file and the repo files from the given directory.

    Args:
        dir_path (Pathlib Path): The path to the directory
    """
    settings_file_local = dir_path / 'auto_git_settings.txt'
    readme_file = dir_path / 'README.md'
    gitignore_file = dir_path / '.gitignore'

    settings_file_local.unlink()
    readme_file.unlink()
    gitignore_file.unlink()


def retrieve_pat():
    """Prompts the user to enter it's Private Access Token to GitHub.


    Returns:
        string: The Private Access Token
    """
    pat = input(PROMPT_PAT)
    return pat


def get_endpoint(end_point, pat):
    """Preform a GET http request to the end_point of BASE_URL (GitHub API), with the access token pat.

    Args:
        end_point (string): The end-point in the rest API BASE_URL
        pat (string): The Private Access Token of the user

    Raises:
        ConnectionError: Raised when the respones' status code is not ok.

    Returns:
        python-object: Loaded-json response - Dictionary/array/etc
    """
    url = f"{API_BASE_URL}{end_point}"

    headers = {
        "Authorization": f"token {pat}"
    }

    r = requests.get(url, headers=headers)

    if not r.ok:
        print(ERR_STATUS_CODE.format(r.status_code,
                                     requests.status_codes._codes[r.status_code]))
        raise ConnectionError

    try:
        loaded_json = json.loads(r.text)
    except:
        print(ERR_PARSE_JSON)
        raise

    return loaded_json


def post_endpoint(end_point, pat, payload):
    """Preform a POST http request to the end_point of BASE_URL (GitHub API),
       with the access token pat and the body

    Args:
        end_point (string): The end-point in the rest API of BASE_URL
        pat (string): The Private Access Token of the user
        payload (dictionary): Data to transfer with the POST method

    Raises:
        ConnectionError: Raised when the respones' status code is not ok.

    Returns:
        python-object: Loaded-json response - Dictionary/array/etc
    """
    url = f"{API_BASE_URL}{end_point}"

    headers = {
        "Authorization": f"token {pat}"
    }

    r = requests.post(url, headers=headers, json=payload)

    if not r.ok:
        print(ERR_CREATE_REMOTE)
        print(ERR_STATUS_CODE.format(r.status_code,
                                     requests.status_codes._codes[r.status_code]))
        raise ConnectionError

    try:
        loaded_json = json.loads(r.text)
    except:
        print(ERR_CREATE_REMOTE)
        raise

    return loaded_json


async def push_changes(file_to_track):
    """Every INTERVAL, check if any changes took place in the directory, and push them if there where.  

    Args:
        file_to_track (Pathlib Path): Path to the dominant file we want to track. 
    """
    dir_path = file_to_track.parent
    settings_file = dir_path / 'auto_git_settings.txt'
    settings_dict = json.loads(settings_file.read_text())

    print(MSG_START_TRACKING.format(settings_dict['file_name']))

    repo = Repo(dir_path)

    while True:
        await asyncio.sleep(INTERVAL_SECONDS)

        if repo.is_dirty(untracked_files=True):

            repo.git.add('.')
            repo.index.commit(MSG_COMMIT.format(settings_dict['count_commits'],
                                                time.asctime(time.localtime())))
            repo.remotes.origin.push()

            settings_dict['count_commits'] += 1
            settings_json = json.dumps(settings_dict)
            settings_file.write_text(settings_json)
            print(MSG_CHANGE_RECORDED.format(time.asctime(time.localtime())))


def start_track(raw_file_path):
    """The main function that drives the program.
       Start a tracking session on a given file

    Args:
        raw_file_path (string): Path to the file to track
    """
    if not system_is_configured():
        first_config()

    file_to_track = Path(raw_file_path)

    if not dir_is_initiated(file_to_track.parent):
        new_track(raw_file_path)

    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(push_changes(file_to_track))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print(MSG_END_TRACKING)
        # maybe update some settings here?
        loop.close()


def write_settings_local(settings_file, settings_json, readme_file, readme,
                         gitignore_file, ignores):
    """Write content in settings-file and git repo files

    Args:
        settings_file (Pathlib Path): settings-file to write in
        settings_json (string): Content to write in settings-file (json format)
        readme_file (Pathlib Path): Path to README.md file
        readme (string): Content to write in README file
        gitignore_file (Pathlib Path): Path to .gitignore file
        ignores (string): Content to write in .gitignore file
    """
    settings_file.write_text(settings_json)
    readme_file.write_text(readme)
    gitignore_file.write_text(ignores)


def first_init_add_commit_push(dir_path, ssh_url):
    """Initialize a new local git repository in the directory.
       Add all file to it and commit them.
       Create a new remote-tracking-branch 'master'.
       Push the repo to the fresh already created GitHub repository.

    Args:
        dir_path (Pathlib Path): Path to the directory
        ssh_url (string): Remote repository ssh-url
    """
    new_repo = Repo.init(path=dir_path, mkdir=False)

    new_repo.git.add('.')
    new_repo.index.commit('Initial commit.')

    new_repo.create_head('master').checkout()

    try:
        origin = new_repo.create_remote('origin', url=ssh_url)
    except:
        print(ERR_CREATE_REMOTE)
        sys.exit()

    new_repo.git.push("--set-upstream", origin, new_repo.head.ref)


def new_track(raw_file_path):
    """Configure a new file directory to be ready to be tracked.
       Create settings and GitHub files.
       Create a remote repository on GitHub
       Create a local repository and push it to the remote on GitHub.

    Args:
        raw_file_path (string): Path to the file to be tracked
    """
    file_to_track = Path(raw_file_path)
    dir_path = file_to_track.parent
    settings_file_local = dir_path / 'auto_git_settings.txt'
    readme_file = dir_path / 'README.md'
    gitignore_file = dir_path / '.gitignore'

    initiate_settings_local_dir(
        settings_file_local, readme_file, gitignore_file)

    repo_name = input(PROMPT_REPO_NAME)

    payload = {
        "name": f"{repo_name}",
        "private": "true"
    }

    settings_dict_global = json.loads(SETTINGS_FILE_GLOBAL.read_text())

    try:
        response_dict = post_endpoint("/user/repos",
                                      settings_dict_global['PAT'], payload)
    except:
        cleanup_settings_local(dir_path)
        sys.exit()

    settings_dict_local = {
        "file_name": f"{file_to_track.name}",
        "repo_name": f"{repo_name}",
        "ssh_url": f"{response_dict['ssh_url']}",
        "https_url": f"{response_dict['clone_url']}",
        "count_commits": 1
    }

    write_settings_local(settings_file_local, json.dumps(settings_dict_local),
                         gitignore_file, "auto_git_settings.txt",
                         readme_file, f"# {repo_name}")

    first_init_add_commit_push(dir_path, settings_dict_local['ssh_url'])

    print(MSG_END_NEW_TRACK)


def first_config():
    """Configure the user's computer to be ready to use the program.
       Create global settings file with user's PAT, user_name and email.
       Globally Configure git user's credentials on the machine.
    """
    try:
        initiate_settings_global()
    except:
        sys.exit()

    pat = retrieve_pat()

    try:
        response_dict = get_endpoint("/user", pat)
    except:
        cleanup_settings_global()
        sys.exit()

    user_name = response_dict['login']

    try:
        response_dict = get_endpoint("/user/emails", pat)
    except:
        cleanup_settings_global()
        sys.exit()

    user_email = response_dict[0]['email']

    settings_dict_global = {
        "PAT": f"{pat}",
        "user_name": f"{user_name}",
        "user_email": f"{user_email}"
    }
    settings_json_global = json.dumps(settings_dict_global)
    SETTINGS_FILE_GLOBAL.write_text(settings_json_global)

    ret = subprocess.run(f"git config --global user.name {user_name}")
    ret = subprocess.run(f"git config --global user.email {user_email}")


def main():
    """Usage: auto_git.py [-h] (-c | -f <file_path>)
    """
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--config', action="store_true",
                       help=HELP_FIRST_CONFIG)
    group.add_argument('-f', '--file_path', action="store",
                       type=str, help=HELP_FILE_PATH, metavar=METAVAR_FILE_PATH)

    args = parser.parse_args()

    if args.config:
        first_config()
    else:
        start_track(args.file_path)


if __name__ == "__main__":
    main()

# todo - check the ret
# todo add github to the list of known-hosts. handle it before pushes!
# todo generate ssh key, store it on place, and copy the pass to ssh.txt
# todo give instructions to copy the pat key to pat.txt
# todo add in json all the files we track
# todo add a check for global configuration in the beginning of new-track or start-track
# todo merge the functions new-track and start-track to one.
# todo make sure that github is in known hosts

"""
Useful links:
tutorial GitPython https://www.devdungeon.com/content/working-git-repositories-python
create a dict to json and retrieve https://stackoverflow.com/questions/26745519/converting-dictionary-to-json

"""

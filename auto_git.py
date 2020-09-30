import os
import sys
import json
import time
import asyncio
import requests
from argparse import ArgumentParser
from pathlib import Path
from git import Repo # ? https://www.devdungeon.com/content/working-git-repositories-python
import git
from pprint import pprint
import subprocess

DESCRIPTION = "Track file and automatic push to remote github repository."
EPILOG = "For more information, visit the project page on: https://github.com/yairfine/auto-git"
HELP_FILE_PATH = "The path to the file you want to git."
HELP_START_TRACK = "Sets the program to track an existing repo and file"
HELP_NEW_TRACK = "Sets the program create a new track for a given file"
HELP_FIRST_CONFIG = "Sets the program to first-config mode"
METAVAR_FILE_PATH = "<file_path>"

ERR_PAT_EXISTS = "It's seems like you already configured this system, try to run again with -n/-s flag"

MSG_EXIT = "To stop: press Ctrl+C and wait a few seconds"
MSG_SSH_PAT_CONFIG = """
Make sure you have Git installed (version > 1.5)
2.  Open: Git-Bash
3.  Run: ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
4.  Press enter: Enter a file in which to save the key (/c/Users/you/.ssh/id_rsa):[Press enter]
5.  Press enter: Enter passphrase (empty for no passphrase): [Press enter] (no password needed)
6.  Press enter: [Press enter again] (no password needed)
7.  Run: eval $(ssh-agent -s)
8.  Run: ssh-add ~/.ssh/id_rsa
9.  Run: clip < ~/.ssh/id_rsa.pub   #Copies the contents of the id_rsa.pub file to your clipboard
10. Open: github.com
11. Click: In upper-right corner click profile photo -> settings
12. Click: SSH and GPG keys (side menu)
13. Click: New SSH key or Add SSH key.
14. Title field: write 'auto-git-ssh'
15. Key field: paste your key
16. Click: Add SSH key
17. Click: Developer settings (side menu)
18. Click: Personal access tokens
19. Click: Generate new token
20. Note field: write 'auto-git-pat'
21. Select scopes: 'repo', 'read:user', 'user:email'
22. Click: Generate token
23. COPY!!!: copy the new token (with green V sign aside)
24. Paste: paste the token here and press enter: 
"""

SETTINGS_DIR = Path.home() / 'auto-git-settings'
SETTINGS_FILE_GLOBAL = SETTINGS_DIR / 'auto_git_settings_global.txt'
# SETTINGS_PAT = SETTINGS_DIR / 'pat.txt'
# SETTINGS_USER = SETTINGS_DIR / 'user.txt'

BASE_URL = 'https://api.github.com'


def initiate_settings_dir(settings_dir_path):

    try:
        settings_dir_path.mkdir()

        SETTINGS_FILE_GLOBAL.touch(exist_ok=False)

    except FileExistsError:
        print(ERR_PAT_EXISTS)
        sys.exit()

    pat = input(MSG_SSH_PAT_CONFIG)

    headers = {
        "Authorization" : f"token {pat}"
    }
    

    end_point = "/user"
    url = f"{BASE_URL}{end_point}"

    r = requests.get(url, headers=headers)
    
    if not r.ok:
        print("r is not ok - ", r.status_code)
        sys.exit()
    try:
        response_data = json.loads(r.text)
    except:
        print("cannot parse json")
        sys.exit()

    user_name = response_data['login']

    end_point = "/user/emails"
    url = f"{BASE_URL}{end_point}"

    r = requests.get(url, headers=headers)
    
    if not r.ok:
        print("r is not ok - ", r.status_code)
        sys.exit()
    try:
        response_data = json.loads(r.text)
    except:
        print("cannot parse json")
        sys.exit()
        
    user_email = response_data[0]['email']

    settings_dict_global = {
        "PAT" : f"{pat}",
        "user_name" : f"{user_name}",
        "user_email" : f"{user_email}"
    }
    
    settings_json = json.dumps(settings_dict_global)
    SETTINGS_FILE_GLOBAL.write_text(settings_json)

    ret = subprocess.run(f"git config --global user.name {user_name}")
    ret = subprocess.run(f"git config --global user.email {user_email}")

    # * todo create a username and email file!
    # * todo config them --global !!!
    # todo add github to the list of known-hosts. handle it before pushes!

async def push_changes(file_to_track):
    dir_path = file_to_track.parent
    settings_file = dir_path / 'auto_git_settings.txt'
    settings_dict = json.loads(settings_file.read_text())

    print(f"Started tracking changes on file '{settings_dict['file_name']}'")
    print(MSG_EXIT)

    repo = Repo(dir_path)

    while True:
        await asyncio.sleep(7)
        
        if repo.is_dirty(untracked_files=True):
            
            repo.git.add('.')
            repo.index.commit(f"commit no.{settings_dict['count_commits']} - {time.asctime(time.localtime())}")
            repo.remotes.origin.push()

            settings_dict['count_commits'] += 1
            settings_json = json.dumps(settings_dict)
            settings_file.write_text(settings_json)
            print("A change was recorded")


def start_track(raw_file_path):
    file_to_track = Path(raw_file_path)

    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(push_changes(file_to_track))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Tracking session has ended")
        # maybe update some settings here?
        loop.close()


    # * todo create a time based loop, for checking every minuet if a file was changed
    # * todo add, commit, and push changes
    # * todo add count the number of the repos
    # todo add in json all the files we track 

def new_track(raw_file_path):
    file_to_track = Path(raw_file_path)
    dir_path = file_to_track.parent

    try:
        settings_file = dir_path / 'auto_git_settings.txt'
        readme_file = dir_path / 'README.md'
        gitignore_file = dir_path / '.gitignore'
        settings_file.touch(exist_ok=False)
        readme_file.touch(exist_ok=False)
        gitignore_file.touch(exist_ok=False)

    except FileExistsError:       
        print("It's seems like you already intiated this directory, try to run again with -s flag")
        sys.exit()

    repo_name = input("Please enter your new repository name: ")

    json_data = {
    "name" : f"{repo_name}",
    "private" : "true"
    }
    
    settings_json_global = SETTINGS_FILE_GLOBAL.read_text()
    settings_dict_global = json.loads(settings_json_global.read_text())


    headers = {
        "Authorization" : f"token {settings_dict_global['PAT']}"
    }

    end_point = "/user/repos"

    url = f"{BASE_URL}{end_point}"

    r = requests.post(url, headers=headers, json=json_data)
    
    if r.status_code != 201:
        print("an error accord while trying create the repo on github")
        sys.exit()

    try:
        response_data = json.loads(r.text)
    except:
        print("an error accord while trying create the repo on github")
        sys.exit()
        
    ssh_url = response_data['ssh_url']
    https_url = response_data['clone_url']

    settings_dict = {
        "file_name" : f"{file_to_track.name}",
        "repo_name" : f"{repo_name}",
        "ssh_url" : f"{ssh_url}",
        "https_url" : f"{https_url}",
        "count_commits" : 1
    }
    settings_json = json.dumps(settings_dict)
    settings_file.write_text(settings_json)

    gitignore_file.write_text("auto_git_settings.txt")
    readme_file.write_text(f"# {repo_name}")

    new_repo = Repo.init(path=dir_path, mkdir=False)
    # new_repo = Repo(path=dir_path)

    new_repo.git.add('.')
    new_repo.index.commit('Initial commit.')

    new_repo.create_head('master').checkout()

    try:
        origin = new_repo.create_remote('origin', url=settings_dict['ssh_url'])

    except:
        print(' ~~~ Error creating remote ~~~ ')
        sys.exit()

    new_repo.git.push("--set-upstream", origin, new_repo.head.ref)  
    
    

    # * create a dict to json and retrieve https://stackoverflow.com/questions/26745519/converting-dictionary-to-json
    # * create settings file with the repo name and repo ssh https URI 
    # * todo touch README.md
    # * todo touch .gitignore file
    # * todo git init add commit
    # * todo create new ssh remote tracking branch
    # todo and than start_track()
    

def first_config():
    
    initiate_settings_dir(SETTINGS_DIR)

    # todo generate ssh key, store it on place, and copy the pass to ssh.txt
    
    # todo give instructions to copy the pat key to pat.txt

    # todo 



def main():
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', '--first-config', action="store_true", help=HELP_FIRST_CONFIG)
    group.add_argument('-n', '--new-track', action="store", type=str, help=HELP_NEW_TRACK, metavar=METAVAR_FILE_PATH)
    group.add_argument('-s', '--start-track', action="store", type=str, help=HELP_START_TRACK, metavar=METAVAR_FILE_PATH)

    # parser.add_argument("file_path", help=HELP_FILE_PATH, metavar=METAVAR_FILE_PATH)

    args = parser.parse_args()

    if args.start_track is not None:
        start_track(args.start_track)
    
    elif args.new_track is not None:
        new_track(args.new_track)
    
    elif args.first_config is not None:
        first_config()


if __name__ == "__main__":
    main()
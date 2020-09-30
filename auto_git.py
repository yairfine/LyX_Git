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

DESCRIPTION = "Track file and automatic push to remote github repository."
EPILOG = "For more information, visit the project page on: github.com/yairfine/auto-git"
HELP_FILE_PATH = "The path to the file you want to git."
HELP_START_TRACK = "Sets the program to track an existing repo and file"
HELP_NEW_TRACK = "Sets the program create a new track for a given file"
HELP_FIRST_CONFIG = "Sets the program to first-config mode"
METAVAR_FILE_PATH = "<file_path>"

ERR_PAT_EXISTS = "It's seems like you already configured this system, try to run again with -n/-s flag"

MSG_EXIT = "To stop: press Ctrl+C and wait a few seconds"

SETTINGS_DIR = Path.home() / 'auto-git-settings'
SETTINGS_SSH = SETTINGS_DIR / 'ssh.txt'
SETTINGS_PAT = SETTINGS_DIR / 'pat.txt'
SETTINGS_USER = SETTINGS_DIR / 'user.txt'

def initiate_settings_dir(settings_dir_path):
    
    try:
        settings_dir_path.mkdir()

        SETTINGS_SSH.touch(exist_ok=False)
        SETTINGS_PAT.touch(exist_ok=False)

    except FileExistsError:
        print(ERR_PAT_EXISTS)
        sys.exit()

    # todo pat = input("Please enter you Private Token Authenticator: ")
    # SETTINGS_PAT.write_text(pat ,encoding=UTF-8)
    
    # todo create a username and email file!
    # todo config them --global !!!
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
    
    pat = SETTINGS_PAT.read_text()

    headers = {
        "Authorization" : f"token {pat}"
    }

    base_url = 'https://api.github.com'
    end_point = "/user/repos"

    url = f"{base_url}{end_point}"

    r = requests.post(url, headers=headers, json=json_data)
    
    if r.status_code != 201:
        print("an error accord while trying create the repo on github")
        sys.exit()

    try:
        response_data = r.json()
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
    group.add_argument('-s', '--start-track', action="store", type=str, help=HELP_START_TRACK)
    group.add_argument('-n', '--new-track', action="store", type=str, help=HELP_NEW_TRACK)
    group.add_argument('-c', '--first-config', action="store_true", help=HELP_FIRST_CONFIG)

    # parser.add_argument("file_path", help=HELP_FILE_PATH, metavar=METAVAR_FILE_PATH)

    args = parser.parse_args()

    if args.start_track is not None:
        start_track(args.start_track)
    
    elif args.new_track is not None:
        new_track(args.new_track)
    
    #todo first config no need for path
    elif args.first_config is not None:
        first_config()


if __name__ == "__main__":
    main()
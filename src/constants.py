from pathlib import Path

INTERVAL_SECONDS = 40

DESCRIPTION = "Track file and automatic push to remote github repository."
EPILOG = "For more information, visit the project page on: https://github.com/yairfine/auto-git"
HELP_FILE_PATH = "the path to the file you want to track"
HELP_FIRST_CONFIG = "configure system and exit"
HELP_NEW_TRACK = "initiate a new tracking configuration for a given file"
HELP_START_TRACK = "start tracking a given file and it's directory"
METAVAR_FILE_PATH = '"<file_path>"'

ERR_SETTINGS_GLOBAL_EXISTS = """It's seems like you already configured this system,
try to run again with -f flag"""
ERR_CREATE_REMOTE = ' ~~ Error creating remote repo ~~ '
ERR_SETTINGS_LOCAL_EXISTS = """It's seems like you already initiated this directory, please check your
auto-git-settings file to see if it's not empty."""
ERR_PARSE_JSON = " ~~ Error parsing json ~~ "
ERR_STATUS_CODE = "Respone code is not ok - {} - {}"

MSG_END_NEW_TRACK = "Done preparing for a new track"
MSG_START_TRACKING = """Started tracking changes on file '{}'
To stop: press Ctrl+C and wait a minute"""
MSG_END_TRACKING = "Tracking session has ended"
MSG_CHANGE_RECORDED = "A change was recorded - {}"
MSG_COMMIT = "commit no.{} - {}"
MSG_SUCCESS_CONFIG = "Config was successful !"

PROMPT_PAT = """Welcome to auto-git!
Please paste your Private Accesses Token here
Your PAT: """
PROMPT_REPO_NAME = """You've never tracked this directory before.
Please enter a NAME for new remote repository: """

SETTINGS_DIR_GLOBAL = Path.home() / 'auto-git-settings'
SETTINGS_FILE_GLOBAL = SETTINGS_DIR_GLOBAL / 'auto_git_settings_global.txt'

API_BASE_URL = 'https://api.github.com'
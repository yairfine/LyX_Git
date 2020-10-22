# Automatic 'gitting' for textual files

## Summery
This program automatically track changes of textual files, such as `.lyx`, and push them to a github repository. <br/>
Easily keep track your files and control versions with the git version control.

## Install

### Dependencies
* Windows OS
* Python 3, installed packages:
    * gitpython
    * requests
* Git (version > 1.5)
* GitHub account
    * SSH key (__with no passphrase__) configured with your GitHub account 
    * PAT (Private Access Token) - __with scopes: repo, user__ 

For SSH and PAT, follow this tutorials: </br>
[Connecting to GitHub with SSH](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/connecting-to-github-with-ssh) </br>
[Creating a personal access token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token)</br>


### Configure
Make sure you have all dependencies. </br>
Clone the repo, using:
```
git clone git@github.com:yairfine/auto-git.git
```

Run the program in `--config` mode:
```
python auto_git.py --config
```
Paste your PAT in the auto_git.py prompt <br/>

You are good to go!

## Usage
Start your first tracking session:
```
python auto_git.py --file-path <file_to_track_path>
```

![coding gif](https://media.giphy.com/media/l4FGvUYI0tETAQwGk/giphy.gif)

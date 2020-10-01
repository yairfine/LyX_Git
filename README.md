# Automatic 'gitting' for textual files

## Summery
This program automatically track changes of textual files, such as `.lyx`, and push them to a github repository. <br/>
Easily keep track your files and control versions with the git version control.

## Install
### dependencies
* Python 3
* Git (version > 1.5)

### Configure

Clone the repo, using:
```
git clone https://github.com/yairfine/auto-git.git
```

Run the program in first configuration mode:
```
python auto_git.py --first-config
```
Follow these orders: <br/>

1.  Open: Git-Bash <br/>
2.  Run: ssh-keygen -t rsa -b 4096 -C "your_email@example.com" <br/>
3.  Press enter: Enter a file in which to save the key (/c/Users/you/.ssh/id_rsa):[Press enter] <br/>
4.  Press enter: Enter passphrase (empty for no passphrase): [Press enter] (no password needed) <br/>
5.  Press enter: [Press enter again] (no password needed) <br/>
6.  Run: eval $(ssh-agent -s) <br/>
7.  Run: ssh-add ~/.ssh/id_rsa <br/>
8.  Run: clip < ~/.ssh/id_rsa.pub   #Copies the contents of the id_rsa.pub file to your clipboard <br/>
9.  Open: github.com <br/>
10. Click: In upper-right corner click profile photo -> settings <br/>
11. Click: SSH and GPG keys (side menu) <br/>
12. Click: New SSH key or Add SSH key. <br/>
13. Title field: write 'auto-git-ssh' <br/>
14. Key field: paste your key <br/>
15. Click: Add SSH key <br/>
16. Click: Developer settings (side menu) <br/>
17. Click: Personal access tokens <br/>
18. Click: Generate new token <br/>
19. Note field: write 'auto-git-pat' <br/>
20. Select scopes: 'repo', 'read:user', 'user:email' <br/>
21. Click: Generate token <br/>
22. COPY: copy the new token (with green V sign aside) <br/>
23. Paste: paste the token in the auto_git.py prompt <br/>

// here need to add github to known hosts.

Start your first tracking session:
```
python auto_git.py --new-track <file_to_track_path>
```


## Usage
![coding gif](https://media.giphy.com/media/l4FGvUYI0tETAQwGk/giphy.gif)
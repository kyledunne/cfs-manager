import os, sys, webbrowser
from dropbox import DropboxOAuth2FlowNoRedirect
from pydrive.auth import GoogleAuth
from boxsdk import OAuth2

sys.path.insert(0, os.path.split(os.path.abspath(__file__))[0])
os.chdir(os.path.split(os.path.abspath(__file__))[0])
from manager import fs_classes
from box_wrapper import split_tokens

def filesystem_list(fs_classes):
    print("\nSecondly, the system needs to know which cloud storage providers you use. \nDo you use...")
    chosen = []
    for fs in fs_classes:
        question = fs[0] +"?  [y/n]  "
        choice = input(question).lower()
        if (choice == 'y') or (choice == 'yes'):
            chosen.append(fs[0])
            print(fs[0], "added.")
        else:
            print(fs[0], "cancelled.")
    return chosen

def pcloud_setup(config):
    print("""
    In the current version of CFS_Manager, OAuth for pCloud is not yet supported.
    As such, if you wish to use pCloud, you will need to enter your pCloud password each time you connect.
    (CFS_Manager will never store your password or transmit it to any party other than pCloud itself.)
    However, this setup process will save your email, so you won't need to enter it in future.
    """)
    username = input("Email:  ").strip().strip('"').strip("'").strip()
    #Strip quotes and any space either inside or outside the quotes
    #Don't trust user inputs not to be awful
    config.write('pCloud ::: '+username+'\n')

def dbox_setup(config):
    print("""
    Authorizing CFS_Manager to access your Dropbox account will require your webbrowser.
    An authorization page will be opened on Dropbox's website.
    You'll need to click 'Allow', then paste the code here.
    """)
    cont = input("To continue, enter any letter:  ")
    if cont:
        auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
        authorize_url = auth_flow.start()
        webbrowser.open(authorize_url)
        auth_code = input("Enter the authorization code here: ").strip().strip('"').strip("'").strip()
        config.write('Dropbox ::: '+auth_code+'\n')
    else:
        print("Dropbox setup cancelled")

def gdrive_setup(config):
    print("""
    Authorizing CFS_Manager to access your Google Drive account will require your webbrowser.
    An authorization page will be opened on Google Drive's website.
    You'll need to allow access for your account, then you'll be redirected.
    """)
    cont = input("To continue, enter any letter:  ")
    if cont:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("gdrive_credentials.txt")
        config.write('Google Drive\n')
    else:
        print("Google Drive setup cancelled")

def _box_setup(config):
    print("""
    Authorizing CFS_Manager to access your Box account will require your webbrowser.
    An authorization page will be opened on Box's website.
    After allowing access for your account, you'll be redirected to a page that fails to load.
    You'll need to copy the url of that page into this window to finish the authorization.
    """)
    cont = input("To continue, enter any letter:  ")
    if cont:
        oauth = OAuth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        auth_url, csrf_token = oauth.get_authorization_url('http://localhost:2772')
        webbrowser.open(auth_url)
        csrf_token, auth_code = split_tokens()
        access_token, refresh_token = oauth.authenticate(auth_code)
        config.write('Box (no drop) ::: '+ access_token +'<:>'+ refresh_token +'\n')
    else:
        print("Box setup cancelled")

def setup_switch(fs, config):
    if fs == 'pCloud':
        pcloud_setup(config)
    elif fs == 'Dropbox':
        dbox_setup(config)
    elif fs == 'Google Drive':
        gdrive_setup(config)
    elif fs == 'Box (no drop)':
        _box_setup(config)

def main():
    welcome = "\nWelcome to CFS_Manager's setup and configuration!\n"
    welcome += "There are just a few things you need to do to make sure your virtual filesystem is set up correctly.\n"
    print(welcome)
    download_query = "Firstly, where would you like to store files you download by default?\n"
    download_query += "If you would like to use your downloads folder, please copy the complete path into this prompt.\n"
    download_query += "(You can always choose a different location for a given file when downloading.)\n"
    download_query += "Download location:  "
    with open('system_config.txt', 'w') as config:
        response = input(download_query).strip().strip('"').strip("'").strip()
        config.write('Downloads ::: '+response+'\n')
        fs_list = filesystem_list(fs_classes)
        for fs in fs_list:
            setup_switch(fs, config)
    print("\nThank you for setting up CFS_Manager. You can now access your files using the 'cfsm' system command.")
    print("If this is your first time using CFS_Manager, try entering 'help' once the command line is open.")

if __name__ == "__main__":
    main()
import os
import sys
import json

config = {
    "session": "",
    "username": "",
    "target_user": "",
    "whitelistEnabled": False,
    "whitelist": []
}

def run_server():
    if sys.platform == "win32":
        os.system('python server.py')
    elif sys.platform == "linux" or sys.platform == "darwin":
        os.system(' sudo python3 server.py')
    else:
        print("Unsupported OS.")

def main():
    if os.path.exists('config.json'):
        print("Found config.json, starting server...")
        run_server()
    else:
        print("No config.json found, running setup...")

        print("Installing packages...")
        os.system('pip install asyncio scratchattach')

        print("Setup:")
        config["session"] = input("Enter your session id (get it from https://scratch.mit.edu/): ")
        config["username"] = input("Enter your Scratch username: ")
        config["target_user"] = input("Enter the username of the account you want to monitor comments on: ")
        whitelist = input("Do you want to enable the whitelist? (y/n): ")
        if whitelist.lower() == "y":
            config["whitelistEnabled"] = True
            print("Enter the usernames you want to whitelist, one per line. Enter a blank line to finish.")
            while True:
                user = input("Username: ")
                if user == "":
                    break
                config["whitelist"].append(user)
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("Setup complete! Starting server...")
        run_server()

if __name__ == "__main__":
    main()
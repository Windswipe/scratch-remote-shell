import scratchattach as scratch3
import json
import datetime

import asyncio
from typing import Callable, Optional, Awaitable

config = {
    "username": "USERNAME HERE",
    "session": "SESSION ID HERE",
    "target_user": "griffpatch",
    "whitelistEnabled": False,
    "whitelist": ["username1", "username2"],  # Only used if whitelistEnabled is True
    "commentsSynced": []  # List of comment IDs that have already been processed
}

sessuion = None
boot_time = datetime.datetime.now()

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)
    
def setup_scratch_session():
    global session, config
    try:
        config = load_config()
    except Exception as e:
        print("Failed to load config:", e)
        exit(1)
    print("Config loaded.")
    print("Logging in...")
    session = scratch3.login_by_id(config["session"], username=config["username"])
    print("Logged in as", config["username"])

async def poll_scratch_comments(username: str, callback: Callable[[dict], Awaitable[None]], interval: int = 30):
        """
        Polls the Scratch profile for new comments and fires callback when a new comment is posted.
        :param username: Scratch username to monitor
        :param callback: Async function to call with the new comment dict
        :param interval: Polling interval in seconds
        """
        last_comment_id: Optional[int] = None
        print(f"Monitoring comments for Scratch user: {username}")
        user = session.connect_user(username)
        while True:
            try:
                comments = user.comments(limit=10)
                if comments:
                    print(f"Fetched {len(comments)} comments.")
                    for j in comments:
                        timestamp = str.split(j.datetime_created, "T")
                        timestamp = str.split(timestamp[0], "-")
                        timestamp = datetime.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))
                        # Only process comments created after boot_time
                        threshold = boot_time - datetime.timedelta(days=1)
                        if str(j.id) not in config["commentsSynced"] and timestamp > threshold:
                            await callback({
                                'author': {'username': j.author_name},
                                'content': j.content,
                                'id': j.id,
                                "comment_obj": j
                            })
                            config["commentsSynced"].append(str(j.id))
                            with open('config.json', 'w') as f:
                                json.dump(config, f, indent=4)
            except Exception as e:
                raise e
            await asyncio.sleep(interval)

async def parse_comment(comment):
    username = comment.get('author', {}).get('username')
    content = comment.get('content')
    id = comment.get('id')
    print(f"Processing comment by {comment.get('author', {}).get('username')}: {comment.get('content')}")
    if config["whitelistEnabled"]:
        if username not in config["whitelist"]:
            print(f"{username} is not whitelisted. Ignoring comment.")
            return
    output = await run_shell_command(content)
    comment_obj = comment.get("comment_obj")
    comment_obj.reply(f"@{username} Command output:\n{output}")
    print(f"Replied to comment ID {comment.get('id')}")
    

async def run_shell_command(command: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode() + stderr.decode()
    

if __name__ == "__main__":
    setup_scratch_session()
    asyncio.run(poll_scratch_comments(config["target_user"], parse_comment))

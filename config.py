# For local development, you can untrack this file and substitute your personal keys/paths
# Run `git update-index --skip-worktree config.py` to make it untracked, then add your own configuration as needed
# If you want to make a change to the actual configuration of the production environment, you can run:
# `git update-index --no-skip-worktree config.py` to make it tracked again and push up your changes to GitHub

import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ADMIN_LICHESS_TOKEN = os.environ["ADMIN_LICHESS_TOKEN"]
FIREFOX_BINARY = os.environ["FIREFOX_BIN"]
GECKDRIVER_PATH = os.environ["GECKODRIVER_PATH"]

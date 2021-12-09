import os

LOG_LEVEL = int(os.environ["LOG_LEVEL"])
LOG_FILE = open(os.environ["LOG_FILE"], "w")
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]


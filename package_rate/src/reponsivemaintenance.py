from datetime import datetime
from config import *

NUM_SECONDS_IN_MONTH = 60*60*24*30 * 3
NUM_SECONDS_IN_WEEK = 60*60*24*7

if LOG_LEVEL == 1 or LOG_LEVEL == 2: # pragma: no cover
    LOG_FILE.write("Setting global variables\n")

def responsive(commits):
    numCommits = len(commits)

    if numCommits < 10:
        return 0

    commitDate = commits[0]["commit"]["author"]["date"]
    commitDate = datetime.strptime(commitDate, '%Y-%m-%dT%H:%M:%SZ')

    if LOG_LEVEL == 1: # pragma: no cover
        LOG_FILE.write("Processing input data\n")
    elif LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Decoding timestamps from API response\n")

    dateOneMonthAgo = datetime.now().timestamp() - NUM_SECONDS_IN_MONTH
    dateOneMonthAgo = datetime.fromtimestamp(dateOneMonthAgo)

    dateOneWeekAgo = datetime.now().timestamp() - NUM_SECONDS_IN_WEEK
    dateOneWeekAgo = datetime.fromtimestamp(dateOneWeekAgo)

    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Making calculations on last commit data\n")

    if commitDate < dateOneMonthAgo:
        lastCommitScore = 0
    elif commitDate > dateOneWeekAgo:
        lastCommitScore = 1
    else:
        lastCommitScore = (commitDate - dateOneMonthAgo) / (dateOneWeekAgo - dateOneMonthAgo)

    timeSum = 0
    last = 0
    first = True
    for c in commits:
        cdt = c["commit"]["author"]["date"]
        cdt = datetime.strptime(cdt, '%Y-%m-%dT%H:%M:%SZ').timestamp()
        if first:
            first = False
            last = cdt
            continue
        timeSum += last - cdt
        last = cdt

    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Calculating average time between commits\n")

    commitFreq = timeSum / (numCommits - 1)

    if commitFreq < NUM_SECONDS_IN_WEEK:
        commitFrequencyScore = 1
    elif commitFreq > NUM_SECONDS_IN_MONTH:
        commitFrequencyScore = 0
    else:
        commitFrequencyScore = 1 - (commitFreq - NUM_SECONDS_IN_MONTH) / (NUM_SECONDS_IN_WEEK - NUM_SECONDS_IN_MONTH)

    if LOG_LEVEL == 2 or LOG_LEVEL == 1:
        LOG_FILE.write("Assigning scores\n")

    return 0.5 * commitFrequencyScore + 0.5 * lastCommitScore
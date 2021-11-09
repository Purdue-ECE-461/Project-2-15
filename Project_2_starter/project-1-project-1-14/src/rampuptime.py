# https://arxiv.org/pdf/2106.12239.pdf
from math import log
import requests
from datetime import datetime
from src.config import *

NUM_SECONDS_IN_YEAR = 60 * 60 * 24 * 365

STAR_WEIGHT = 0.5
README_WEIGHT = 0.5

INSTALLKEYS = ["## install", "## setup"]

def calcScore(starScore, readmeScore):
    return starScore * STAR_WEIGHT + readmeScore * README_WEIGHT

def checkInstallHeaderInLine(line):
    line = line.lower()
    for key in INSTALLKEYS:
        if key in line:
            return True
    return False

def rampuptime(repoDir, numStars, max_stars, commitsUrl):
    starScore = log(numStars + 1, 10) / log(max_stars + 1, 10)

    if LOG_LEVEL > 1: # pragma: no cover
        LOG_FILE.write("Getting score of star watchers\n")

    repoFiles = os.listdir(repoDir)

    hasReadme = False
    readmeFileName = None
    for file in repoFiles:
        fileLow = file.lower()
        if "readme." in fileLow:
            readmeFileName = file
            hasReadme = True
            break

    readmeScore = 0

    numLineScore = 0
    hasInstallScore = 0
    numCodeBlockScore = 0
    latestReadmeUpdateScore = 0

    if LOG_LEVEL > 1: # pragma: no cover
        LOG_FILE.write("Getting score of readme quality\n")

    if hasReadme:
        with open(f"{repoDir}/{readmeFileName}") as readmeFile:
            lines = readmeFile.readlines()
            numLines = len(lines)

            if numLines < 500 and numLines > 50:
                numLineScore = numLines / 500
            elif numLines >= 500:
                numLineScore = 1

            hasInstall = False
            numCodeBlocks = 0
            for l in lines:
                if not hasInstall and checkInstallHeaderInLine(l):
                    hasInstall = True

                if "```" in l:
                    numCodeBlocks += 1

            if hasInstall:
                hasInstallScore = 1

            numCodeBlocks /= 2
            if numCodeBlocks > 10:
                numCodeBlockScore = 1
            elif numCodeBlockScore <= 10:
                numCodeBlockScore = numCodeBlocks / 10

        response = requests.get(f"{commitsUrl}?path={readmeFileName}&page=1&per_page=1", headers={'Authorization': f"token {GITHUB_TOKEN}"})
        commit = response.json()
        if(len(commit) != 0):
            commitDate = commit[0]["commit"]["author"]["date"]
            commitDate = datetime.strptime(commitDate, '%Y-%m-%dT%H:%M:%SZ')
            dateOneYearAgo = datetime.now().timestamp() - NUM_SECONDS_IN_YEAR
            dateOneYearAgo = datetime.fromtimestamp(dateOneYearAgo)

            if commitDate > dateOneYearAgo:
                latestReadmeUpdateScore = 1

        readmeScore = 0.35 * hasInstallScore + 0.35 * numCodeBlockScore + 0.2 * numLineScore + 0.1 * latestReadmeUpdateScore

    fullscore = calcScore(starScore, readmeScore)
    if LOG_LEVEL > 0:
        LOG_FILE.write(f"Got rampuptime score: {fullscore}\n")

    return fullscore
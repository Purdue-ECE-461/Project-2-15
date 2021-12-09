import sys
import requests
from config import *
import shutil
import zipfile
import numpy

from rampuptime import rampuptime
from busfactor import busFactor, busFactorCalculations
from license import licenseCheck
from reponsivemaintenance import responsive
from correctness import correctness

MOST_STARS = 333506

GITHUB_URL = "github.com"
NPMJS_URL_COM = "npmjs.com"
NPMJS_URL_ORG = "npmjs.org"

NPMJS_GET_LINK = "https://registry.npmjs.org/"
GITHUB_REPO_URL = "https://api.github.com/repos"
GITHUB_MOST_STARS_URL = "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars"
GITHUB_MOST_ISSUES = "https://api.github.com/search/repositories?q=open_issues:%3E1&sort=open_issues"

TEMP_PATH = "tmp"

def getPackageFiles(org, package, defaultBranch):
    #get the zip file
    response = requests.get(f"https://api.github.com/repos/{org}/{package}/zipball/{defaultBranch}",
                            headers={'Authorization': f"token {GITHUB_TOKEN}"})

    os.makedirs(f"{TEMP_PATH}/{package}", exist_ok=True)

    # write zipfile to temp folder
    with open(f"{TEMP_PATH}/{package}/{defaultBranch}.zip", "wb") as outzip:
        outzip.write(response.content)

    # unzip file
    with zipfile.ZipFile(f"{TEMP_PATH}/{package}/{defaultBranch}.zip", mode="r") as packageZip:
        packageZip.extractall(f"{TEMP_PATH}/{package}/{defaultBranch}")

    return f"{TEMP_PATH}/{package}/{defaultBranch}"

def removeTmpFiles():
    if os.path.exists(TEMP_PATH):
        shutil.rmtree(TEMP_PATH)

def calcMetrics(githubURL):
    githubLink = githubURL.split(GITHUB_URL)[1].split("/")
    org = githubLink[1]
    package = githubLink[2].replace(".git", "")

    if LOG_LEVEL > 1: # pragma: no cover 
        LOG_FILE.write(f"Getting metadata for {org}/{package}\n")
    basePackageLink = f"{GITHUB_REPO_URL}/{org}/{package}"
    response = requests.get(basePackageLink, headers={'Authorization': f"token {GITHUB_TOKEN}"})
    if response.status_code != 200:
        return None

    metadata = response.json()
    commitsURL = metadata["commits_url"].replace("{/sha}", "")

    if LOG_LEVEL > 1: # pragma: no cover
        LOG_FILE.write(f"Getting commit for {org}/{package}\n")
    response = requests.get(commitsURL + "?limit=10", headers={'Authorization': f"token {GITHUB_TOKEN}"})
    commits = response.json()

    numStars = metadata["stargazers_count"]
    numIssues = metadata["open_issues_count"]

    defaultBranch = metadata["default_branch"]

    if LOG_LEVEL > 1: # pragma: no cover
        LOG_FILE.write(f"Getting package files for {org}/{package}\n")
    packagePath = getPackageFiles(org, package, defaultBranch)
    repoFiles = os.listdir(packagePath)
    packagePath = packagePath + "/" + repoFiles[0]

    if "package.json" not in os.listdir(packagePath):
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"{githubURL} not a npm packagae since it does not have a package.json")
        return None

    try:
        if LOG_LEVEL > 1: # pragma: no cover
            LOG_FILE.write(f"Running license check {org}/{package}\n")
        licenseScore = licenseCheck(packagePath)
        licenseScore = round(licenseScore, 2)
    except:
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"ERROR IN GETTING LICENSE SCORE FOR {githubLink}")
        licenseScore = -1

    try:
        if LOG_LEVEL > 1: # pragma: no cover
            LOG_FILE.write(f"Running rampuptime check {org}/{package}")
        rampupScore = rampuptime(packagePath, numStars, MOST_STARS, commitsURL)
        rampupScore = round(rampupScore, 2)
    except:
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"ERROR IN GETTING RAMPUP SCORE FOR {githubLink}")
        rampupScore = -1

    try:
        if LOG_LEVEL > 1: # pragma: no cover
            LOG_FILE.write(f"Running busFactor check {org}/{package}")
        busFactorScore = busFactor(basePackageLink)
        busFactorScore = round(busFactorScore, 2)
    except:
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"ERROR IN GETTING BUSFACTOR SCORE FOR {githubLink}")
        busFactorScore = -1

    try:
        if LOG_LEVEL > 1: # pragma: no cover
            LOG_FILE.write(f"Running responsive maintenance check {org}/{package}")
        responsiveMaintenanceScore = responsive(commits)
        responsiveMaintenanceScore = round(responsiveMaintenanceScore, 2)
    except:
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"ERROR IN GETTING RESPONSIVE MAINTENANCE SCORE FOR {githubLink}")
        responsiveMaintenanceScore = -1

    try:
        if LOG_LEVEL > 1: # pragma: no cover
            LOG_FILE.write(f"Running correctness check {org}/{package}")
        correctnessScore = correctness(packagePath, numIssues)
        correctnessScore = round(correctnessScore, 2)
    except:
        if LOG_LEVEL > 0: # pragma: no cover
            LOG_FILE.write(f"ERROR IN GETTING CORRECTNESS SCORE FOR {githubLink}")
        correctnessScore = -1


    output = [licenseScore, rampupScore, busFactorScore, responsiveMaintenanceScore, correctnessScore]

    removeTmpFiles()
    return output

def getGithubLink(url):
    if GITHUB_URL in url:
        repourl = url
    elif NPMJS_URL_COM in url or NPMJS_URL_ORG in url:
        packageName = url.split("package/")[1]
        response = requests.get(f"{NPMJS_GET_LINK}{packageName}")
        if response.status_code != 200:
            if LOG_LEVEL > 0: # pragma: no cover
                LOG_FILE.write(f"NPMJS package named \"{packageName}\" not found\n")
            return None

        package_data = response.json()
        try:
            repo = package_data["repository"]
        except KeyError:
            if LOG_LEVEL > 0: # pragma: no cover
                LOG_FILE.write(f"Repo link for package named \"{packageName}\" not found\n")
            return None

        repourl = repo["url"]
    else:
        return None

    if "//" in repourl:
        repourl = repourl.split("//")[1]

    return repourl

def overallScore(data):
    if LOG_LEVEL > 1: # pragma: no cover
        LOG_FILE.write(f"Calculating overall score\n")
    
    for i in range(5):
        if data[i] == -1:
            data[i] = 0
    totalScore = data[1]*0.20 + data[2]*0.25 + data[3]*0.35 + data[4]*0.2
    totalScore *= data[0]
    return totalScore

def getScore(filename):
    listOfList = []
    totalScoreList = []

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            githubLink = getGithubLink(line)
            if githubLink == None:
                continue
            metricRes = calcMetrics(githubLink)
            if metricRes != None:
                metricRes.append(line)
                metricRes.append(line)
                totalScore = overallScore(metricRes)
                totalScore = round(totalScore, 2)
                totalScoreList.append(totalScore)
                metricRes.append(totalScore)
                listOfList.append(metricRes)
                # print([line, metricRes])
        A = numpy.array(listOfList)
        B = numpy.array(totalScoreList)

        inds = B.argsort()[::-1]

        sorted_a = A[inds]

    return sorted_a


def run(filename):
    sorted_a = getScore(filename)
    output = []
    for module in sorted_a:
        output.append(f"{module[5]} {module[6]} {module[1]} {module[4]} {module[2]} {module[3]} {module[0]}")
        
# print(filename)
    return output

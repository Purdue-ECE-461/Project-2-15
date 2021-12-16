import requests
from src.config import *


def APIcall(basePackageLink):
    base_url = f"{basePackageLink}/contributors?per_page=100"
    response = requests.get(base_url,  headers={'Authorization': f"token {GITHUB_TOKEN}"})
    if LOG_LEVEL == 1: # pragma: no cover
        LOG_FILE.write("API response recieved\n")
    elif LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("API response recieved in form of json\n")
    data = response.json()        
    return data


def contributorCount(data):
    freqList = []

    if LOG_LEVEL == 1: # pragma: no cover  
        LOG_FILE.write("Processing response data\n")
    elif LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Processing response data\n")
        LOG_FILE.write("Building list of contributors\n")
    
    for contributor in data:
        freqList.append(contributor["contributions"])
    return freqList

'''
Metrics:
    1. No. of contributors: 70%
    2. Contribuitions of contributors: 30%
'''

def busFactorCalculations(freqList):
    
    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Checking if there are 0 contributors\n")

    if len(freqList) == 0:
        if LOG_LEVEL == 1 or LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("There are 0 contributors\n")
            if LOG_LEVEL == 2: # pragma: no cover
                LOG_FILE.write("Exiting Bus Factor calculations\n")            
        return 0


    numMultiplier = 0.70
    contribuitionMultiplier = 0.30
    contribuitionScore = 1 #assume perfect distribuition
    mean = sum(freqList)/len(freqList)
    num = len(freqList)

    if num == 100:
        numScore = 1
    else:
        numScore = float(num / 100)
    

    if LOG_LEVEL == 1: # pragma: no cover
        LOG_FILE.write("Performing Calculations\n")
    elif LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Calculating number of contributors\n")
        LOG_FILE.write("Calculating number of contributions by each contributors\n")
    #add score for mean
    counter = 0 #num of people who contribute more than other and hence affect bus factor more
    for contribution in freqList:
        if contribution < mean:
            break
        counter += 1

    if num < 100:
        temp = float(counter / num)
    else:
        temp = float(counter / 100)


    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Performing Calculations\n")

    numScore *= numMultiplier
    contribuitionScore -= temp
    contribuitionScore *= contribuitionMultiplier
    
    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Applying weights to resuluts\n")

    return numScore + contribuitionScore

def busFactor(basePackageLink):
    if LOG_LEVEL == 1 or LOG_LEVEL == 2:
        LOG_FILE.write("Initiating Bus Factor Calculations\n")
        LOG_FILE.write("Making API Call to GitHub API\n")
    data = APIcall(basePackageLink)
    freqList = contributorCount(data)
    score = busFactorCalculations(freqList)

    if LOG_LEVEL == 1 or LOG_LEVEL == 2:
        LOG_FILE.write("Bus Factor calculations completed")

    return score

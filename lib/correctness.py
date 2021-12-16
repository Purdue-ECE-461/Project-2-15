import os
import subprocess
import random
from src.config import *

def getjs(packagePath):
    outlist = []
    dirlist = os.listdir(packagePath)
    for f in dirlist:
        if f == "node_modules" or f == "packages":
            continue
        if os.path.isdir(f"{packagePath}/{f}"):
            outlist += getjs(f"{packagePath}/{f}")
        elif len(f) >= 3 and f[-3:] == ".js":
            outlist.append(f"{packagePath}/{f}")

    return outlist

def correctness(packagePath, issues):
    numJs = getjs(packagePath)
    index = []
    nosyntaxProblems = 1

    random.seed(2)

    if len(numJs) < 10:
        index = random.sample(range(0, len(numJs)), len(numJs))
    else:
        index = random.sample(range(0, len(numJs)), 10)

    if LOG_LEVEL == 1 or LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("JS files  \n")

    for x in range(len(index)):
        command = "cd node-v14.18.0-linux-x64/bin/;"
        command += "eslint ../../" + numJs[index[x]] + " -c .eslintrc.json --no-eslintrc --quiet"

        
        my_subprocess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        subprocess_return = my_subprocess.stdout.read()
        subprocess_return = str(subprocess_return)

        if LOG_LEVEL == 1 or LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Runned linter\n")

        if "problem" in subprocess_return:
            nosyntaxProblems = 0
            break

    issues_Score = 1 - issues/(133 + (2*227))

    if issues_Score > 1:
        issues_Score = 1

    if issues_Score < 0:
        issues_Score = 0

    return (issues_Score * nosyntaxProblems)


# if __name__ == "__main__":
#     correctness("tmp/browserify/master", 20)
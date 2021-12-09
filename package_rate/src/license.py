import json
from config import *

def compatibilityCheck(licenseInfo):
    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("License data recieved")
    compatiblePermissive = ["MIT", "X11", "BSD-3-Clause", "BSD-2-Clause"]
    compatibleWeakCopyleft = ["LGPL-2.1"]

    if LOG_LEVEL == 1 or LOG_LEVEL == 2:
        LOG_FILE.write("Checking license information for compatibility\n")
        LOG_FILE.write("License compatibility check complete\n")
    if licenseInfo in compatiblePermissive:
        return float(1)
    elif licenseInfo[:8] == compatibleWeakCopyleft[0]:
        return 0.75
    else:
        return float(0)

   
def licenseCheck(repoDir):
    packageJsonFile = repoDir + "/package.json"
    
    if LOG_LEVEL == 2: # pragma: no cover
        LOG_FILE.write("Checking if package.json file exists\n")
        LOG_FILE.write("Package.json file found\n")

    with open(packageJsonFile) as pfile:
        packageJson = json.load(pfile)

        if LOG_LEVEL == 1: # pragma: no cover
            LOG_FILE.write("Accessing package.json file\n")

        elif LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Accessing package.json file to get data\n")


    if "license" not in packageJson:
        return 0

    if LOG_LEVEL == 1: # pragma: no cover
            LOG_FILE.write("Checking if license info exists\n")
            
    elif LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Checking if the license information is present in package.json file\n")


    liceseType = packageJson["license"]
            
    if LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Checking if current SPDX representation followed\n")


    if not isinstance(liceseType, str):
        liceseType = liceseType["type"]
        if LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Deprecated representation followed\n Accessing license information using altenate method\n")

    if LOG_LEVEL == 1 or LOG_LEVEL == 2:
        LOG_FILE.write("License data obtained\n")
        if LOG_LEVEL == 2: # pragma: no cover
            LOG_FILE.write("Passing license information to compatibility checker\n")
            
    return compatibilityCheck(liceseType)

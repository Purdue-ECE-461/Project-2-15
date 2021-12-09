import subprocess

def runCmd(cmd):
    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    subp.stdout.read()

def installDeps():
    runCmd("pip3 install --user -r src/requirements.txt")

    runCmd("wget https://nodejs.org/dist/v14.18.0/node-v14.18.0-linux-x64.tar.xz")
    runCmd("tar -xf node-v14.18.0-linux-x64.tar.xz")
    runCmd("rm -rf node-v14.18.0-linux-x64.tar.xz")

    runCmd("cd node-v14.18.0-linux-x64/bin;./npm install -g eslint")


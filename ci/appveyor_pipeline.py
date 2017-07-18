import os, argparse

# Please read pipeline_instructions.py before working on this file
CONFIGURATION = os.environ["CONFIGURATION"] if "CONFIGURATION" in os.environ else "Release"
GIT_REPO_NAME = os.environ["APPVEYOR_PROJECT_NAME"]
ARCH = os.environ["ARCH"]
BINTRAY_REPO_MSI = os.environ["BINTRAY_REPO_MSI"]
BINTRAY_REPO_NUGET = os.environ["BINTRAY_REPO_NUGET"]
BINTRAY_REPO_CHOCO = os.environ["BINTRAY_REPO_CHOCO"]
BINTRAY_SUBJECT = os.environ["BINTRAY_SUBJECT"]
BINTRAY_USER = os.environ["BINTRAY_USER"]
BINTRAY_KEY = os.environ["BINTRAY_KEY"]
#CHOCO_KEY = os.environ["CHOCO_KEY"]
PKG_VERSION = os.environ["APPVEYOR_BUILD_VERSION"]
PKG_NAME = GIT_REPO_NAME + "-" + ARCH + "-" + PKG_VERSION

parser = argparse.ArgumentParser()
parser.add_argument("-step_name")
args = parser.parse_args()

def before_build():
  go_msi_path = "C:\Program Files\go-msi"
  wix_path = "C:\Program Files (x86)\WiX Toolset v3.11\bin"
  os.environ["PATH"] +=  os.pathsep + go_msi_path + os.pathsep + wix_path

def build_script():
  generator_name = '"' + os.environ["CMAKE_GENERATOR"] + '"'
  os.system("md build")
  os.chdir("build")
  os.system("cmake -G " + generator_name + " ../src")
  os.system("cmake --build . --config " + CONFIGURATION)
    
def after_build():
  package_msi()
  package_nupkg() 
  
def deploy_script():
  print("Downloading JFrog CLI")
  os.system("curl -fsSk -o jfrog.exe -L https://api.bintray.com/content/jfrog/jfrog-cli-go/%24latest/jfrog-cli-windows-amd64/jfrog.exe?bt_package=jfrog-cli-windows-amd64")
  
  os.system("jfrog bt config --user " + BINTRAY_USER + " --key " + BINTRAY_KEY + " --licenses MIT")
  bintray_path = "pool" + "/" + PKG_NAME[0] + "/" + GIT_REPO_NAME + "/"
  
  msi_upload_suffix = PKG_NAME + ".msi " + BINTRAY_SUBJECT + "/" + BINTRAY_REPO_MSI + " " + bintray_path
  nupkg_upload_suffix = PKG_NAME + ".nupkg " + BINTRAY_SUBJECT + "/" + BINTRAY_REPO_NUGET + " " + bintray_path
  choco_upload_suffix = PKG_NAME + ".nupkg " + BINTRAY_SUBJECT + "/" + BINTRAY_REPO_CHOCO + " " + bintray_path
  
  upload_bintray(msi_upload_suffix)
  upload_bintray(nupkg_upload_suffix)
  upload_bintray(choco_upload_suffix)
  #upload_choco()

def package_msi():
  print("Packaging MSI")
  package_cmd=(
  "go-msi make" + 
  " --path msi-creation-data.json" +
  " --version " + PKG_VERSION +
  " --msi " +  PKG_NAME + ".msi")
  print("MSI command : " + package_cmd)
  os.system(package_cmd)
    
def package_nupkg():
  print("Packaging NUPKG")
  package_cmd=(
  "go-msi choco" + 
  " --path msi-creation-data.json" +
  " --version " + PKG_VERSION +
  " --input " + PKG_NAME + ".msi"
  " --output " + PKG_NAME + ".nupkg")
  print("NUPKG command : " + package_cmd)
  os.system(package_cmd)
  
def upload_bintray(upload_cmd_suffix):
  upload_cmd_prefix = "jfrog bt upload --override --publish "
  print("Uploading file to Bintray with command: " + upload_cmd_prefix + upload_cmd_suffix)
  os.system(upload_cmd_prefix + upload_cmd_suffix)
  
def upload_choco():
  choco_upload_cmd = "choco push -k=" + CHOCO_KEY + " " + NUPKG_NAME
  print("Uploading file to Chocolatey with command: " + choco_upload_cmd)
  os.system(choco_upload_cmd)
  
  
# This actually executes the step, must be after all methods are defined.
exec(args.step_name + "()")
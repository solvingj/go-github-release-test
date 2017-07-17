import os, argparse

# Please read pipeline_instructions.py before working on this file

CONFIGURATION = os.environ["CONFIGURATION"] if "CONFIGURATION" in os.environ else "Release"
GIT_REPO_NAME = os.environ["GIT_REPO_NAME"]
ARCH = os.environ["ARCH"]
BINTRAY_USER = os.environ["BINTRAY_USER"]
BINTRAY_KEY = os.environ["BINTRAY_KEY"]
BINTRAY_REPO_DEB = os.environ["BINTRAY_REPO_DEB"]
BINTRAY_REPO_RPM = os.environ["BINTRAY_REPO_RPM"]
BINTRAY_REPO_TARGZ = os.environ["BINTRAY_REPO_TARGZ"]
BINTRAY_REPO_CONAN = os.environ["BINTRAY_REPO_CONAN"]
PKG_VERSION = os.environ["PKG_VERSION"]
PKG_NAME = GIT_REPO_NAME + "-" + ARCH + "-" + PKG_VERSION

parser = argparse.ArgumentParser()
parser.add_argument("-step_name")
args = parser.parse_args()

def before_install():
  os.system("add-apt-repository 'deb https://dl.bintray.com/solvingj/public-deb unstable main'")

def install():
  os.system("apt-get update")
  os.system("apt-get install --allow-unauthenticated fakeroot go-bin-deb changelog")

def script():
  os.system("mkdir build && cd build")
  os.chdir("build")
  os.system("cmake ../src && cmake --build . --config " + CONFIGURATION)

def after_success():
  package()
  deploy()

def package():
  package_deb()
  package_rpm()
  package_targz()
  package_conan()
  
def deploy():
  print("Downloading JFrog CLI")
  os.system("curl -fL https://getcli.jfrog.io | sh")
  os.system("./jfrog bt config --user " + BINTRAY_USER + " --key " + BINTRAY_KEY + " --licenses MIT")
  
  bintray_path = "pool" + "/" + PKG_NAME[0] + "/" + PKG_NAME + "/"
  
  deb_upload_suffix = "--deb " + PKG_NAME + ".deb " + BINTRAY_REPO_DEB + "/" + bintray_path
  rpm_upload_suffix = PKG_NAME + ".rpm " + BINTRAY_REPO_RPM + "/" + bintray_path
  targz_upload_suffix = PKG_NAME + ".tar.gz " + BINTRAY_REPO_RPM + "/" + bintray_path
  conan_upload_suffix = PKG_NAME + ".zip " + BINTRAY_REPO_RPM + "/" + bintray_path
  
  upload_bintray(deb_upload_suffix)
  upload_bintray(rpm_upload_suffix)
  #upload_bintray(targz_upload_suffix)
  #upload_bintray(conan_upload_suffix)
  
def package_deb():
  print("Packaging DEB")
  package_cmd=(
  "go-bin-deb generate" +
  " --file deb-creation-data.json" +
  " --version " + PKG_VERSION + 
  " --arch " + ARCH + 
  " -o " + PKG_NAME + ".deb")
  print("DEB command : " + package_cmd)
  os.system(package_cmd)
    
def package_rpm():
  print("Packaging RPM")
  package_cmd=(
  "go-bin-rpm generate" +
  " --file rpm-creation-data.json" +
  " --version " + PKG_VERSION + 
  " --arch " + ARCH + 
  " -o " + PKG_NAME + ".rpm")
  
  print("RPM command : " + package_cmd)
  os.system("docker run -v %cd%:/mnt/travis solvingj/go-bin-rpm /bin/sh -c \"" + package_cmd + "\"")
  
def package_targz():
  print("No instructions for conan packaging tar.gz")
  
def package_conan():
  print("No instructions for conan packaging yet")
    
def upload_bintray(upload_cmd_suffix):
  print("Uploading files to Bintray with suffix: " + upload_cmd_suffix)
  upload_cmd_prefix = "./jfrog bt upload --override --publish "
  os.system(upload_cmd_prefix + upload_cmd_suffix)
    
# This actually executes the step, must be after all methods are defined.
exec(args.step_name + "()")
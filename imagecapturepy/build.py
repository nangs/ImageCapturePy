from shutil import copy2
from distutils.spawn import find_executable

import grp,pwd,os,glob,sys
import subprocess,errno,re,pip

import modules.name.user as user
import modules.lsb.release as lsb
import modules.logging.logger as logger

class Build():

    def __init__(self):
        if not self.dirExists(self.rootDirectory()):
            self.mkdirP(self.rootDirectory())

    def homeDirectory(self):
        return "/home/" + user.name()

    def rootDirectory(self):
        return "/home/" + str(user.name()) + "/.imagecapture"

    def pictureDirectory(self):
        return "/home/" + str(user.name()) + "/.imagecapture/pictures"

    def incrementBackupNumber(self):
        number = []
        os.chdir(self.pictureDirectory)
        for file_name in glob.glob("*.png"):
            capture = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            number.append(int(capture.group(2)))
        return int(max(number))

    def copyFile(self,source,destination):
        if not self.fileExists(destination) and self.fileExists(source):
            copy2(source,destination)
        elif self.fileExists(destination) and self.fileExists(source):
            logger.log("WARN","File already exists! Backing up before copying to destination!")
            copy2(source,destination + ".backup")
            copy2(source,destination)

    def fileExists(self,file_name):
        return os.path.isfile(file_name)

    def createFile(self,file_name):
        if not self.fileExists(file_name):
            open(file_name, 'w')

    def chown(self,dir_path,user_name,group_name):
        uid = pwd.getpwnam(user_name).pw_uid
        gid = grp.getgrnam(group_name).gr_gid
        os.chown(dir_path, uid, gid)

    def chmod(self,dir_path,mode):
        os.chmod(dir_path, mode)

    def dirExists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdirP(self,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and dirExists(dir_path):
                pass
            else:
                raise

    def executableExists(self,executable_name):
        return find_executable(executable_name)

    def executableVersion(self,executable_name):
        if str(executable_name) == 'opencv_version' and executableExists(executable_name):
            comm = subprocess.Popen([executable_name], shell=True, stdout=subprocess.PIPE)
            if comm is not None:
                return str(comm.stdout.read())
        if self.executableExists(executable_name):
            comm = subprocess.Popen([executable_name + ' --version'], shell=True, stdout=subprocess.PIPE)
            if comm is not None:
                logger.log("INFO","" + str(comm.stdout.read()))
        else:
            logger.log("WARN","Executable does not exist!")

    def systemQueryCommand(self):
        if self.packageManager() == 'rpm':
            system_query_command = 'rpm -qa'
        elif self.packageManager() == 'dpkg':
            system_query_command = 'dpkg --list'
        elif self.packageManager() == 'eix':
            system_query_command = 'eix --only-names'
        return system_query_command

    def installSystemPackage(self,package_name):
        if self.packageManager() == 'rpm':
            system_install_command = 'sudo yum --assumeyes install ' + str(package_name) + ' 2> /dev/null'
        elif self.packageManager() == 'dpkg':
            system_install_command = 'sudo apt-get --force-yes --yes install ' + str(package_name) + ' 2> /dev/null'
        elif self.packageManager() == 'eix':
            system_install_command = 'sudo emerge -v install ' + str(package_name) + ' 2> /dev/null'
        comm = subprocess.Popen([system_install_command], shell=True, stdout=subprocess.PIPE)
        if comm is not None:
            logger.log("INFO","Installed system package - " + str(package_name))

    def grepSystemPackages(self,package_name):
        comm = subprocess.Popen([self.systemQueryCommand()], shell=True, stdout=subprocess.PIPE)
        if comm is not None:
            package = re.search(str(package_name), str(comm.stdout.read()), re.I | re.M)
            if package is not None:
                return package.group()

    def listPipPackages(self):
        return pip.get_installed_distributions()

    def grepPipPackage(self,package_name):
        package = re.search(str(package_name),str(self.listPipPackages()), re.I | re.M)
        if package is not None:
            return package.group()

    def listSystemPackages(self):
        packages = []
        comm = subprocess.Popen([self.systemQueryCommand()], shell=True, stdout=subprocess.PIPE)
        if comm is not None:
            packages.append(comm.stdout.read())
        return packages

    def packageManager(self):
        package_manager = {
            'rpm': ('centos','fedora','scientific','opensuse'),
            'dpkg': ('debian','ubuntu','linuxmint')
            'eix': ('gentoo')}
        for key,value in package_manager.items():
            manager = re.search(lsb.release().lower(),str(value), re.I | re.M)
            if manager is not None:
                return key
        if manager is None:
            return False

    def pamD(self):
        if self.packageManager() == 'rpm':
            return 'rpm/password-auth','rpm/password-auth'
        elif self.packageManager() == 'dpkg':
            return 'dpkg/common-auth','dpkg/mdm.conf'
        elif self.packageManager() == 'eix':
            return 'eix/system-login','eix/system-login'

    def pythonVersion(self):
        python_version = re.search('\d\.\d', str(sys.version), re.I | re.M)
        if python_version is not None:
            return python_version.group()

    def psAUX(self,regex):
        process = subprocess.Popen(['ps','aux'], stdout=subprocess.PIPE)
        if process is not None:
            regex = re.search(str(regex), str(process.stdout.read()), re.I | re.M)
            if regex is not None:
                return regex.group()

    def authName(self):
        auth_list  = ('gdm','mdm','slim')
        auth_regex = self.psAUX('/(var|usr)/.*(X|Xorg).*\-auth.[0-9A-Za-z\/:\.\-]*')
        for a in auth_list:
            auth = re.search(str(a), str(auth_regex), re.I | re.M)
            if auth is not None:
                logger.log("INFO","Using Login Manager \"" + str(auth.group() + "\""))
        if auth is None:
            logger.log("ERROR","Login Manager is not supported yet. Here is a list of supported Login Managers.")
            for a in auth_list:
                print("    -> " + str(i))
            sys.exit(1)

if __name__ == '__main__':

    build = Build()
    build.chmod(build.rootDirectory(),0777)
    build.chown(build.rootDirectory(),user.name(),user.name())

    try:

        if not build.packageManager():
            logger.log("ERROR","Your system is not supported. You can add it yourself or submit a pull request via githib.")
            sys.exit(1)

        if not build.pythonVersion() == '2.7':
            logger.log("Only python 2.7 is supported! Exiting now!")
            sys.exit(1)

        build.authName():

        if not build.dirExists(build.pictureDirectory()):
            build.mkdirP(build.pictureDirectory())
            build.chmod(build.pictureDirectory(),0777)
            build.chown(build.pictureDirectory(),user.name(),user.name())
        else:
            logger.log("WARN","Directory \"" + build.pictureDirectory() + "\" " + "exists!")
        if not build.fileExists(build.pictureDirectory() + "/capture1.png"):
            build.createFile(build.pictureDirectory() + "/capture1.png")
            build.chmod(build.pictureDirectory() + "/capture1.png",0775)
            build.chown(build.pictureDirectory() + "/capture1.png",user.name(),user.name())
        else:
            logger.log("WARN","File \"" + build.pictureDirectory() + "/capture1.png\" " + "exists!")
        if not build.fileExists(build.rootDirectory() + "/credentials.conf"):
            build.createFile(build.rootDirectory() + "/credentials.conf")
            build.chmod(build.rootDirectory() + "/credentials.conf",0775)
            build.chown(build.rootDirectory() + "/credentials.conf",user.name(),user.name())
        else:
            logger.log("WARN","File \"" + build.rootDirectory() + "/credentials.conf\" " + "exists!")

        logger.log("INFO","OS release = " + lsb.release())

        for module in build.pamD():
            build.copyFile('build/autologin/' + module,'/etc/pam.d/')

        build.copyFile('imagecapture.py','/usr/local/bin/')
        build.copyFile('build/home/user/.ssh/is_imagecapture_running.sh',build.homeDirectory() + '/.ssh/is_imagecapture_running.sh')
        if build.fileExists('/usr/local/bin/imagecapture.py'):
            build.chmod('/usr/local/bin/imagecapture.py',0775)
            build.chown('/usr/local/bin/imagecapture.py',user.name(),user.name())
        if build.fileExists(build.homeDirectory() + '/.ssh/is_imagecapture_running.sh'): 
            build.chmod(build.homeDirectory() + '/.ssh/is_imagecapture_running.sh',0775)
            build.chown(build.homeDirectory() + '/.ssh/is_imagecapture_running.sh',user.name(),user.name())

        logger.log("INFO","Grabbing system packages now!")
        for package in ['sqlite3','syslog-ng','sendmail-cf','sendmail-devel','procmail','python-dev','python-opencv','opencv-python']:
            if not build.grepSystemPackages(package):
                logger.log("WARN","Installing system package: " + str(package))
                build.installSystemPackage(package)
            else:
                logger.log("WARN","System package: " + str(package) + " is already installed!")

        if not build.executableExists('opencv_version'):
            logger.log("ERROR","OpenCV system package was not found. Please install OpenCV before continuing.")
            sys.exit(1)
        elif not grepPipPackage('opencv-python') and not grepPipPackage('python-opencv'):
            logger.log("ERROR","OpenCV pip package was not found. Please install OpenCV before continuing.")
            sys.exit(1)
        else: 
            logger.log("INFO","Found opencv version " + build.executableVersion('opencv_version'))

    except Exception as exception:
        logger.log("ERROR","Exception exception :- " + str(exception))
        sys.exit(1)
from shutil import copy2

import grp,pwd,os,glob,sys
import subprocess,errno,re

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

    def packageManager(self):
        package_manager = {'rpm': ('centos','fedora'), 'apt': ('debian','ubuntu')}
        for key,value in package_manager.items():
            manager = re.search(lsb.release().lower(),str(value))
            if manager is not None:
                return key

    def pamD(self):
        if self.packageManager() == 'rpm':
            return 'rpm/password-auth','rpm/password-auth'
        elif self.self.packageManager() == 'apt':
            return 'apt/common-auth','apt/mdm.conf'

if __name__ == '__main__':

    build = Build()
    build.chmod(build.rootDirectory(),0777)
    build.chown(build.rootDirectory(),user.name(),user.name())

    try:
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

    except Exception as exception:
        logger.log("ERROR","Exception exception :- " + str(exception))
        sys.exit(1)

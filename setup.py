#!/usr/bin/python

import sys, os
from SoftwareManager.backend.GitClient import GitClient
import subprocess
import shutil 
from colors import red, green, yellow

class Commands():
    help = "help"
    new_repository = "new_repository"
    
    listCommand = [help, new_repository]
    
    @staticmethod
    def inList(arg):
        '''
        '''
        return (arg in Commands.listCommand)

def usage():
    '''
    '''
    print('\nUsage of this script:')
    print('new_repository\t = Create a new software repository')
    print('help\t\t = Display this help')
    print('\n')
    
def new_repository_usage():
    print('\nCommand usage:')
    print('new_repository NAME [LOCATION] [ICON] \n')

def getSetupLocation():
    path = sys.argv[0].split("/")
    
    if len(path) == 1:
        return "."
    
    del path[len(path) - 1]
    return os.path.sep.join(path)
    
    
def print_step(text):
    percent = (100 * print_step.current) / print_step.total 
    print(green("[" + str(percent) + "%] " + text))
    print_step.current += 1
    
print_step.current = 1
print_step.total = 0
    
def print_error(text):
    print(red("[ERROR] " + text))
    
def print_warning(text):
    print(yellow("[WARNING] " + text))
    
# Display usage
if len(sys.argv) == 1 or sys.argv[1] == Commands.help or not Commands.inList(sys.argv[1]) :
    usage()
    exit()
     
# Display new repository usage
if (sys.argv[1] == Commands.new_repository and len(sys.argv) == 2) or (sys.argv[1] == Commands.new_repository and len(sys.argv) > 2 and sys.argv[2] == Commands.help):
    new_repository_usage()
    exit()
     
# Create new repository
if sys.argv[1] == Commands.new_repository :
    print_step.total = 10
    
    print_step("Checking arguments")
        
    # Install directory
    if len(sys.argv) == 4:
        if not os.path.exists(sys.argv[3]):
            print_error("Install directory doesn't exist")
            exit()
        elif not os.path.isdir(sys.argv[3]):
            print_error("Install directory is not a directory")
            exit()
        
    # Name
    repository = sys.argv[2] + GitClient.extension
    if  len(sys.argv) > 3 :
        repository = sys.argv[3] + "/" + repository 
        
    if os.path.exists(repository):
        print_error("Repository " + sys.argv[2] + " already exist at this location")
        exit()
        
    # Icon
    useDefaultIcon = True
    if len(sys.argv) == 5:
        if not os.path.isfile(sys.argv[4]):
            print_warning("Icon is not a regular file, default icon is used")
        else:
            useDefaultIcon = False
            
        
    try :
        print_step("Creating repository directory")
        os.makedirs(repository)
        
        # Create directory which contain git repository
        print_step("Creating directory which contain git repository")
        git_directory = os.path.join(repository, "git")
        if not os.path.exists(git_directory):
            os.makedirs(git_directory)
            
        # Create git repository
        print_step("Creating git repository")
        subprocess.check_call(GitClient.git + " init --bare", cwd=git_directory, shell=True) 
        
        # Clone git repository to install default files
        print_step("Cloning git repository")
        tmp_directory = os.path.join(repository, "tmp")
        try :
            subprocess.check_call(GitClient.git + " clone git tmp", cwd=repository, shell=True)
        except:
            print_error("Cloning step failed")
        
        # Retrieve setup location
        setup_location = os.path.join(getSetupLocation(), "setup")
         
        # Copy default files
        print_step("Copying default files")
        install_file_directory = os.path.join(tmp_directory, ".launcher")
        if not os.path.exists(install_file_directory):
            os.makedirs(install_file_directory)
        
        if useDefaultIcon:
            shutil.copyfile(os.path.join(setup_location, "icon.png"), os.path.join(install_file_directory, "icon.png"))
        else:
            shutil.copyfile(sys.argv[4], os.path.join(install_file_directory, "icon.png"))
            
        shutil.copyfile(os.path.join(setup_location, "config.ini"), os.path.join(install_file_directory, "config.ini"))
        shutil.copyfile(os.path.join(setup_location, "settings.json"), os.path.join(install_file_directory, "settings.json"))
        shutil.copyfile(os.path.join(setup_location, "install.py"), os.path.join(install_file_directory, "install.py"))
        shutil.copyfile(os.path.join(setup_location, "configure.py"), os.path.join(install_file_directory, "configure.py"))
        shutil.copyfile(os.path.join(setup_location, "launch.py"), os.path.join(install_file_directory, "launch.py"))
        shutil.copyfile(os.path.join(setup_location, "update.py"), os.path.join(install_file_directory, "update.py"))
        
        # Commit modification to repository git
        print_step("Pushing modification into git repository")
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "icon.png", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "config.ini", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "settings.json", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "install.py", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "configure.py", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "launch.py", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " add .launcher" + os.path.sep + "update.py", cwd=tmp_directory, shell=True)
        
        subprocess.check_call(GitClient.git + " commit -m 'Software repository creation'", cwd=tmp_directory, shell=True)
        subprocess.check_call(GitClient.git + " push origin master", cwd=tmp_directory, shell=True)
        
        # Remove tmp directory
        print_step("Cleaning temp files")
        shutil.rmtree(tmp_directory)
        
        # Copy software icon
        print_step("Installing icon software")
        if useDefaultIcon:
            shutil.copyfile(os.path.join(setup_location, "icon.png"), os.path.join(repository, "icon.png"))
        else:
            shutil.copyfile(sys.argv[4], os.path.join(repository, "icon.png"))
        
        print_step("Repository " + sys.argv[2] + " created")
    except:
        print_error("Repository creation failed")
        shutil.rmtree(repository)

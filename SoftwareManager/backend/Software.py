'''
Created on 12 juin 2016

@author: chakour
'''
import configparser
import subprocess, os.path, shutil
from SoftwareManager.backend.GitClient import GitClient
from SoftwareManager.utils.Thread import popenAndCall

class Software:
    '''
    Manage software life cycle
    '''
    
    gitClient = GitClient()
    iconExtension = "png"
    
    def __init__(self, address, install_dir, install_file):
        '''
        Constructor
        '''
        self.address = address
        self.name = self.address.split(os.path.sep)
        if len(self.name) == 1:
                self.name = self.address.split("\\")
        self.name = self.name[len(self.name) - 2].split(".")
        self.name = self.name[0]
        self.local_address = os.path.join(install_dir, self.name)
        self.scripts = os.path.join(self.local_address, ".launcher")
        self.install_file = install_file
      
      
    def configure(self, section, key, value):
        '''
        Configure software by calling configure python script
        '''
        # Getting old value
        config_path = os.path.join(self.scripts, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        old_value = config[section][key]

        try :
            cmd = "python configure.py " + section + " " + key + " " + value + " " + old_value
            subprocess.check_call(cmd, cwd=self.scripts, shell=True)

            # Save new value in config file
            config[section][key] = value
            with open(config_path, 'w') as configfile:
                config.write(configfile)

            return True
        except:
            return False
        
    def updateAvailable(self):
        '''
        '''
        return self.gitClient.needUpdate(self.address, self.local_address)
          
          
    def __install_end__(self, options, error):
        if not error : 
            options["button"].text = "Installation end..."
            # Saving installation information
            self.save()
            
            # Create running configuration
            self.createRunningConfig()

            # Patch config.ini file
            self.patchConfig()
            
            options["callback"](options["callback_options"], False)
        else :
            # Suppression du clone
            self.gitClient.remove(self.local_address)
            options["callback"](options["callback_options"], error)
          
    def __install_script__(self, options, error):
        print("Install script")
        if not error : 
            options["button"].text = "Running install script..."
            popenAndCall(self.__install_end__, options, "python install.py", cwd=self.scripts, shell=True)
        else :
            if error.returncode != 128 : # cible existe deja
                # Suppression du clone
                self.gitClient.remove(self.local_address)
            options["callback"](options["callback_options"], error)
        
    def install(self, callback, callback_options, button):
        '''
        Software installation

        Parameters
        ----------
        callback : Function
            Callback to call when installation is completed
        callback_options : List
            Callback's options
        button : kivy.Button
            Button clicked to launch installation
        '''
        print("Installation of " + self.name)
        
        if not self.exist() :
            button.text = "Cloning repository..."
            self.gitClient.clone(self.__install_script__,  {"callback":callback, "callback_options":callback_options, "button":button}, self.address, self.local_address)
        
            
    def createRunningConfig(self):
        '''
        Create running configuration
        '''
        # Get the config.ini path
        config = os.path.join(self.scripts, "config.ini")
        configRunning = os.path.join(self.scripts, "config_running.ini")
        # Copy the config.ini file
        shutil.copyfile(config, configRunning)

    def patchConfig(self):
        '''
        '''
        with open(self.getConfigPath(), 'r') as original: data = original.read()
        with open(self.getConfigPath(), 'w') as modified: modified.write("[software]\nserver=" + self.address + "\n\n" + data)
        
    def launch(self):
        '''
        Start software by calling the launch script
        '''
        try:
            # Calling installation script
            subprocess.Popen("python launch.py", cwd=self.scripts, shell=True)
            return True
        except:
            return False
        
    def update(self):
        '''
        Update software by pulling information from the remote software
        '''
        
        # Est-ce qu'une mise a jour est necessaire ?
        if self.updateAvailable():
            try :
                # Si oui, on effectue la mise a jour
                self.gitClient.applyUpdate(self.local_address)
            
                # Et on appelle le script d'update
                subprocess.check_call("python update.py", cwd=self.scripts, shell=True)
                
                return True
            except:
                return False
        return True
        
    def getName(self):
        '''
        Return the software name
        '''
        return self.name
    
    def getRemoteIcon(self):
        '''
        Return the remote software icon
        '''
        return os.path.join(self.address, "..", "icon." + Software.iconExtension)
        
    def getIcon(self):
        '''
        Return the local software icon
        '''
        return os.path.join(self.scripts, "icon." + Software.iconExtension)
        
    def getConfigPath(self):
        '''
        Return the software configuration path
        '''
        return os.path.join(self.scripts, "config_running.ini")
        
    def getSettingsPath(self):
        '''
        Return the setting structure file used by kivy
        '''
        return os.path.join(self.scripts, "settings.json")
    
    
    def exist(self):
        '''
        Check if the software is already installed
        '''
        file = open(self.install_file, "r")
        installed = file.read().splitlines()
        result = False
        for install in installed :
            if install == self.address:
                print("Software is already installed")
                result = True
                break
        
        file.close()
        return result
        
    def save(self):
        '''
        Save the software installation informations
        '''
        file = open(self.install_file, "a")
        file.write(self.address + '\n')
        file.close()  
        

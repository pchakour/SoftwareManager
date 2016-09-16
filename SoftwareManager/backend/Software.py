'''
Created on 12 juin 2016

@author: chakour
'''
from SoftwareManager.backend.GitClient import GitClient
import subprocess, os.path
from SoftwareManager.utils.Thread import popenAndCall

class Software:
    '''
    classdocs
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
      
      
    def configure(self):
        try :
            subprocess.check_call("python configure.py", cwd=self.scripts, shell=True)
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
            # Sauvegarde 
            self.save()
             
            # Patch le fichier config.ini
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
        Installation du logiciel
        '''
        print("Installation of " + self.name)
        
        if not self.exist() :
            button.text = "Cloning repository..."
            self.gitClient.clone(self.__install_script__,  {"callback":callback, "callback_options":callback_options, "button":button}, self.address, self.local_address)
        
            
    def patchConfig(self):
        '''
        '''
        with open(self.getConfigPath(), 'r') as original: data = original.read()
        with open(self.getConfigPath(), 'w') as modified: modified.write("[software]\nserver=" + self.address + "\n\n" + data)
        
    def launch(self):
        '''
        '''
        try:
            # Appel du script d'installation
            subprocess.Popen("python launch.py", cwd=self.scripts, shell=True)
            return True
        except:
            return False
        
    def update(self):
        '''
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
        '''
        return self.name
    
    def getRemoteIcon(self):
        '''
        '''
        return os.path.join(self.address, "..", "icon." + Software.iconExtension)
        
    def getIcon(self):
        '''
        '''
        return os.path.join(self.scripts, "icon." + Software.iconExtension)
        
    def getConfigPath(self):
        '''
        '''
        return os.path.join(self.scripts, "config.ini")
        
    def getSettingsPath(self):
        '''
        '''
        return os.path.join(self.scripts, "settings.json")
    
    
    def exist(self):
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
        file = open(self.install_file, "a")
        file.write(self.address + '\n')
        file.close()  
        
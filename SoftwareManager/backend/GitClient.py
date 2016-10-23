import threading
import subprocess
import glob
import shutil
import os.path
from SoftwareManager.utils.Thread import popenAndCall

class GitClient:
    """
        Classe d'interface avec le client git
        disponible sur la machine local
    """
    
    extension = ".soft"
    git = "git"
    
    def __init__(self):
        """
            Constructeur
        """


    def __extractCommitId(self, commitId):
        """
            Extraction de l'identifiant d'un commit 
        """
        return str(commitId).split("HEAD", 1)[0].strip()

    @staticmethod
    def isBinary(path):
        try :
            subprocess.check_call(path + " --version", shell=True)
            return True
        except:
            return False
    
    def remove(self, local):
        '''
        '''
        shutil.rmtree(local, ignore_errors=True)
    
    def getRepositories(self, url):
        """ 
            Retourne la liste des repositories
            git disponible a l'adresse donnee
        """
        result = []
        repositories = glob.glob(os.path.join(url, "*" + GitClient.extension))
        for repository in repositories:
            result.append(os.path.join(repository, "git"))
            
        return result
    
    def __clone_checkout__(self, options, error):
        if not error :
            popenAndCall(options["callback"], options["callback_options"], GitClient.git + " checkout update", cwd=options["cwd"], shell=True)
        else :
            options["callback"](options["callback_options"], error)

    def __clone_branch__(self, options, error):
        if not error :
            popenAndCall(self.__clone_checkout__, options, GitClient.git + " branch update", cwd=options["cwd"], shell=True)
        else :            
            options["callback"](options["callback_options"], error)
        
    def clone(self, callback, options, remote, local):
        """
            Clone une repository donnee
        """
        popenAndCall(self.__clone_branch__,  
                     {"cwd":local, "callback":callback, "callback_options": options}, 
                     GitClient.git + " clone \"" + remote + "\" \"" + local + "\"", 
                     shell=True, 
                     cwd=None)


    def applyUpdate(self, local):
        """
            Applique les modifications d'un repository
        """
        if not GitClient.isBinary(GitClient.git) :
            return False
        
        # Creation d'un backup de l'etat actuel
        subprocess.call(GitClient.git + " add -A", cwd=local, shell=True)
        subprocess.call(GitClient.git + " commit -m 'backup_update'", cwd=local, shell=True)

        # Bascule sur le branche "master" et mise a jour de la branche
        subprocess.call(GitClient.git + " checkout master", cwd=local, shell=True)
        subprocess.call(GitClient.git + " pull", cwd=local, shell=True)

        # Bascule sur la branche "update" et merge de la branche "master"
        subprocess.call(GitClient.git + " checkout update", cwd=local, shell=True)
        subprocess.call(GitClient.git + " merge -s recursive -X theirs master -m 'apply_update'", cwd=local, shell=True)

        return True
        
    def needUpdate(self, remote, local):
        """
            Verifie si une mise a jour est disponible
        """
        
        try :
            # Recuperation de l'identifiant du dernier commit local
            localCommitId = self.__extractCommitId(subprocess.check_output(GitClient.git + " ls-remote \"" + local + "\" HEAD", shell=True))
        
            # Recuperation de l'identifiant du dernier commit distant
            remoteCommitId = self.__extractCommitId(subprocess.check_output(GitClient.git + " ls-remote \"" + remote + "\" HEAD", shell=True))
                
            return (localCommitId != remoteCommitId)
        except:
            return False

'''
Created on 11 juin 2016

@author: chakour
'''
from SoftwareManager.backend.GitClient import GitClient

class Repository :
    '''
    classdocs
    '''


    def __init__(self, address):
        '''
        Constructor
        '''
        self.address = address
        self.git = GitClient()
        
        # Recherche des softwares disponibles
        
    def getAllSoftware(self):
        """
        """
        return self.git.getRepositories(self.address)
'''
Created on 11 juin 2016

@author: chakour
'''
from SoftwareManager.backend.Repository import Repository


class RepositoryManager:
    """
    """
        
    def __init__(self):
        """
        """
        self.repositories = {}
        
    def load(self, addresses):
        """
        """
        self.repositories.clear()
        
        # Parcours de la liste des addresses
        for address in addresses:
            self.repositories[address] = Repository(address)
            
    def getAllRepositories(self) :
        """
        """
        return self.repositories
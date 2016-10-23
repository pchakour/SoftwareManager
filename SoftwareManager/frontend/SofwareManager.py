import sys
from kivy.app import App
from kivy.config import ConfigParser
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.lang import Builder
from kivy.uix.listview import ListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line, Point
from kivy.uix.button import Button
from kivy.uix.settings import SettingsWithSidebar, InterfaceWithSidebar,\
    ContentPanel
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from SoftwareManager.backend.RepositoryManager import RepositoryManager
from SoftwareManager.backend.Software import Software
from SoftwareManager.backend.GitClient import GitClient
import subprocess
import os.path
from SoftwareManager.backend.GitClient import GitClient
from SoftwareManager.utils.Thread import popenAndCall
import SoftwareManager


class TabLayout(GridLayout):
    pass

class Item(BoxLayout):
        
    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)

    def addText(self, title, remote):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=title, font_size=18, halign='left'))
        box.add_widget(Label(text="Server address : " + remote, font_size=12, halign='left'))
        self.add_widget(box)
        
    def addIcon(self, url):
        self.add_widget(Image(source=url, size_hint=(None, None), pos=self.pos, size=(50, 50)))
                
    def addButton(self, text, id, on_press):
        self.add_widget(Button(text=text, on_press=on_press, id=id, size_hint=(None, .8), background_color=(1, 1, 1, 0.2)))
            
class SoftwareManagerGui(BoxLayout):
    
    selected_item = ""
    def __init__(self, **kwargs):
        super(SoftwareManagerGui, self).__init__(**kwargs)
        
        self.ids.tab_all_software_id.bind(on_press = self.retrieveAllSoftware)
        self.ids.tab_installed_software_id.bind(on_press = self.retrieveInstalledSoftware)
        
        self.config = ConfigParser()
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config.read(os.path.join(root, 'myconfig.ini'))
        self.ids.settings_id.add_json_panel('Launcher settings', self.config, os.path.join(root, 'settings.json'))
        self.ids.settings_id.on_config_change = self.onConfigChange
        for address in self.getInstalledSoftware():
            software = Software(address, self.getInstallDir(), self.getInstallFile())
            self.addSettingsPanel(software)
            
        
        self.retrieveInstalledSoftware(None)
        
        
    def onConfigChange(self, instance, section, key, value):
        '''
        Callback when change on software configuration are detected

        Parameters
        ----------
        instance : Config
            Software configuration.
        section : String
            Section of the ini configuration file edited
        key : String
            Key of the ini configuration file edited
        value : String
            New value edited in the ini configuration file
        '''
        try :
            software = Software(instance.get("software", "server"), self.getInstallDir(), self.getInstallFile())
            software.configure(section, key, value)
        except:
            # Check if git is executable
            if not GitClient.isBinary(instance.get("git", "binary")) :
                self.error("Can't execute git binary")
        
    def launchSoftware(self, button):
        error = False
        
        self.launch_software = Software(button.id, self.getInstallDir(), self.getInstallFile())
        
        if self.config.get("launcher", "update") == "auto":
            if not self.launch_software.update() :
                self.error("Something wrong when updating software : check your git path")
                
            error = not self.launch_software.launch()
        
        elif self.config.get("launcher", "update") == "popup" and self.launch_software.updateAvailable():
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text='Do you want apply the update ?'))
                        
            buttons = BoxLayout(orientation='horizontal')
            yes = Button(text='yes')
            no = Button(text='no')
            buttons.add_widget(yes)
            buttons.add_widget(no)
            
            content.add_widget(buttons)
            
            popup = Popup(title='Software update available', size_hint=(None, None), size=(400, 200), content=content, auto_dismiss=False)
            no.bind(on_press=popup.dismiss)
            no.bind(on_press=self.noPopup)
            yes.bind(on_press=popup.dismiss)
            yes.bind(on_press=self.yesPopup)
            popup.open()
        else:
            error = not self.launch_software.launch()
        
        if error :
            self.error("Can't launch software")
        
    def info(self, text):
        info =  Popup(title='Information', size_hint=(None, None), size=(400, 200), content=Label(text=text))
        info.open()   
    
    def error(self, text):
        error = Popup(title='An error occured', size_hint=(None, None), size=(400, 200), content=Label(text=text))
        error.open()
            
    def noPopup(self, no):
        if not self.launch_software.launch():
            self.error("Can't launch software")
        
    def yesPopup(self, yes):
        if not self.launch_software.update() :
            self.error("Something wrong when updating software : check your git path")
        else:
            self.info("The software is up to date")
        
        if not self.launch_software.launch():
            self.error("Can't launch software")
        
    def __install_software_callback__(self, options, error):
        if not error :
            software = options["software"]
            self.addSettingsPanel(software)
            self.displaySettingPanel(software)
            self.info("Software " + software.getName() + " installed, you have to configure it")
        else:
            options["button"].text = "Install"
            options["button"].disabled = False
            self.error("Can't install software : " + str(error))
        
    def installSoftware(self, button):
        software = Software(button.id, self.getInstallDir(), self.getInstallFile())
        button.text = "Installing..."
        button.disabled = True
        software.install(self.__install_software_callback__, {"software":software, "button":button}, button);
        
    def configureSoftware(self, button):
        software = Software(button.id, self.getInstallDir(), self.getInstallFile())
        self.displaySettingPanel(software)
        
    def retrieveInstalledSoftware(self, tab):
        self.ids.scroll_installed_software_id.clear_widgets()
        layout = TabLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for address in self.getInstalledSoftware():
            software = Software(address, self.getInstallDir(), self.getInstallFile())
            item = Item()
            item.addIcon(software.getIcon())
            item.addText(software.getName(), address)
            item.addButton(text="Start", id=address, on_press=self.launchSoftware)
            item.addButton(text="Configure", id=address, on_press=self.configureSoftware)
            layout.add_widget(item)
        
        self.ids.scroll_installed_software_id.add_widget(layout)
        
        
    def addSettingsPanel(self, software):
        config = ConfigParser()
        config.read(software.getConfigPath())
        self.ids.settings_id.add_json_panel(software.getName(), config, software.getSettingsPath())
        
    def retrieveAllSoftware(self, tab):
        self.ids.scroll_all_software_id.clear_widgets()
        
        repoManager = RepositoryManager()
        repositories = self.config.get("launcher", "repositories").split(";")
        repoManager.load(repositories)

        print(repoManager.getAllRepositories().values())
        data = []
        for repo in repoManager.getAllRepositories().values() :
            data += repo.getAllSoftware()
            
        layout = TabLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for address in data:
            software = Software(address, self.getInstallDir(), self.getInstallFile())
            item = Item()
            print(software.getRemoteIcon())
            item.addIcon(software.getRemoteIcon())
            item.addText(software.getName(), address)
            if software.exist() :
                item.addButton(text="Update", id=address, on_press=self.updateSoftware)
            else :
                item.addButton(text="Install", id=address, on_press=self.installSoftware)
                
            layout.add_widget(item)
        
        self.ids.scroll_all_software_id.add_widget(layout)
        
                
    def displaySettingPanel(self, software):
        self.ids.pannels.switch_to(self.ids.tab_settings_id);
        for button in self.ids.settings_id.interface.menu.buttons_layout.children:
            if button.text == software.getName():
                print(self.ids.settings_id.interface.menu.selected_uid)
                self.ids.settings_id.interface.menu.selected_uid = button.uid
                button.selected = True
            else:
                button.selected = False
                
    def updateSoftware(self, button):
        software = Software(button.id, self.getInstallDir(), self.getInstallFile())        
        if not software.update():
            self.error("Something wrong when updating software : check your git path")
        else:
            self.info("The software is up to date")
        
    def getInstallFile(self):
        install_dir = self.config.get("launcher", "install_path")
        if  not os.path.isdir(self.config.get("launcher", "install_path")) :
            install_dir = ""
            
        install_file = os.path.join(install_dir, ".installed")
        if not os.path.isfile(install_file): 
            file = open(install_file, "w")
            file.close()
            
        return install_file
    
    def getInstallDir(self):
        return self.config.get("launcher", "install_path")
       
    def getInstalledSoftware(self):
        install_file = self.getInstallFile()
        file = open(install_file, "r")
        installed = file.read().splitlines()
        file.close()
        return installed
                     
class SoftwareManagerApp(App):
    def build(self):
        return SoftwareManagerGui()

    

#from PySide2 import QtWidgets, QtCore, QtGui

import hou
import json
import os
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path
from StyleLoader import style

class quickProjectLogic:
    def __init__(self):
        self.jsonPath = Path(f"{hou.getenv('HOUDINI_USER_PREF_DIR')}/ALTools/Projects.json")
        self.jsonPath.parent.mkdir(parents=True, exist_ok=True) # make sure ALTools folder exists
        self.textPath = "E:/Projects"
        self.startup()

    def startup(self):
        if self.checkJsonExists():
            print("Json Dosnt exist")
            self.checkJsonExists()
        else:
            print("Json Exists")

    def checkJsonExists(self):
        if not os.path.exists(self.jsonPath):
                structure = {
                    "settings": {
                        "author": "",
                        "homeFolder": "",
                        "Style": "Default"
                    },
                    "Projects": {}
                }
                
                with open(self.jsonPath, 'w') as file:  
                    json.dump(structure, file, indent=4)
                    print(f"Created new JSON file at: {self.jsonPath}")


    def saveHipFile(self, project, file, version):
        # === get File Path === #
        self.filePath = Path(f"{self.textPath}/{project}/{project}_{file}_v{version}.hip")
        self.filePath.parent.mkdir(parents=True, exist_ok=True)

        # === save file === #
        self.save = hou.hipFile.save(str(self.filePath),True)
        print(f"Saved File At: {self.filePath}")
    
    def updateJsonSettings(self, setting, value):
        if value == "":
            print("value was blank")
            return

        else:
            with open(self.jsonPath, "r") as file:
                data = json.load(file)

            data["settings"][str(setting)] = value

            with open(self.jsonPath, "w") as file:
                json.dump(data, file, indent=4)



        

class settingsPannel(QtWidgets.QDialog):
    authorChanged = QtCore.Signal(str)
    filePathChanged = QtCore.Signal(str)

    def __init__(self):
        super().__init__(hou.qt.mainWindow())
        self.configure_dialog()
        self.widgets()
        self.layout()

    def configure_dialog(self):
        self.setWindowTitle("Quick Project Settings")
        self.setFixedWidth(240)


    def widgets(self):
        #Stylesheets
        textStyle = style("textLineStyle.qss")
        buttonStyle = style("buttonStyle.qss")
        folderButtonStyle = style("folderButtonStyle.qss")

        # Author Widget
        self.author = QtWidgets.QLineEdit()
        self.author.setStyleSheet(textStyle)
        self.author.setPlaceholderText("Author")

        # Project Folder Widget
        self.projectFolderlayout = QtWidgets.QHBoxLayout()

        folderButton = QtWidgets.QPushButton()
        icon = hou.ui.createQtIcon("BUTTONS_chooser_file")
        folderButton.setIcon(icon)
        folderButton.setStyleSheet(folderButtonStyle)
        folderButton.clicked.connect(self.chooseProjectFolder)

        self.projectFolder = QtWidgets.QLineEdit()
        self.projectFolder.setStyleSheet(textStyle)
        self.projectFolder.setPlaceholderText("Project Folder")

        self.projectFolderlayout.addWidget(self.projectFolder)
        self.projectFolderlayout.addWidget(folderButton)

        # buttons 
        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.setStyleSheet(buttonStyle)
        self.saveButton.clicked.connect(self.saveClicked)

        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.setStyleSheet(buttonStyle)
        self.cancelButton.clicked.connect(self.cancelClicked)

    def layout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        textEditLayout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()
    

        textEditLayout.addWidget(self.author)
        textEditLayout.addLayout(self.projectFolderlayout)

        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)

        self.mainLayout.addLayout(textEditLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.setLayout(self.mainLayout)


    def saveClicked(self):
        self.authorChanged.emit(self.author.text())
        self.filePathChanged.emit(self.projectFolder.text())
        self.accept()

    def cancelClicked(self):
        self.close()

    def chooseProjectFolder(self):
        # Open Houdini's native folder chooser
        folder_path = hou.ui.selectFile(
            title="Select Project Folder",
            file_type=hou.fileType.Directory,
            chooser_mode=hou.fileChooserMode.Read
        )
        
        if folder_path:
            self.projectFolder.setText(folder_path)

class quickProjectUi(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(hou.qt.mainWindow())
    
    #settings/title
        self.menuBar()

    #save Bar
        self.saveWidgets()
        self.saveBarLayout()

    #file Tree
        self.fileTreeWidgets()
        self.fileTreeLayout()

    #main Layout
        self.mainLayout()

    #logic
        self.connector()
        self.logic = quickProjectLogic()
        self.show()


    # -----------------------------------------------------------------
    # UI Setup
    # -----------------------------------------------------------------


    def menuBar(self):
        #styles
        settingsStyle = style("settingsIconStyle.qss")
        titleStyle = style("titleStyle.qss")

        #widgets
        self.settingsCog = QtWidgets.QPushButton()
        icon = hou.ui.createQtIcon("MISC_generic")
        self.settingsCog.setIcon(icon)
        #self.settingsCog.setMaximumWidth(35)
        self.settingsCog.setMinimumHeight(35)
        self.settingsCog.setStyleSheet(settingsStyle)
        title = QtWidgets.QLabel("Quick Project")
        title.setStyleSheet(titleStyle)
        
        #Layout
        self.menuBarLayout = QtWidgets.QHBoxLayout()
        self.menuBarLayout.addWidget(title)
        self.menuBarLayout.addWidget(hou.qt.Separator())
        self.menuBarLayout.addWidget(self.settingsCog)


    def saveWidgets(self):

        #StyleSheets
        buttonsStyle = style("buttonStyle.qss")
        textLineStyle = style("textLineStyle.qss")  
        versionStyle = style("versionStyle.qss")

        #seperator 
        self.setperator = hou.qt.Separator()

        #save Button
        self.save = QtWidgets.QPushButton("Save")
        self.save.setMinimumWidth(70)
        self.save.setMaximumWidth(70)
        self.save.setStyleSheet(buttonsStyle)

        #Save as Button
        self.saveAs = QtWidgets.QPushButton("Save As")
        self.saveAs.setMinimumWidth(70)
        self.saveAs.setMaximumWidth(70)
        self.saveAs.setStyleSheet(buttonsStyle)

        #Project name
        self.projectName = QtWidgets.QLineEdit()
        self.projectName.setStyleSheet(textLineStyle)
        self.projectName.setMaximumWidth(150)
        self.projectName.setPlaceholderText("Project")

        #File Name
        self.fileName = QtWidgets.QLineEdit()
        self.fileName.setStyleSheet(textLineStyle)
        self.fileName.setPlaceholderText("Hip File Name")

        #Version Counter
        version = 0
        self.version = QtWidgets.QLabel(f"v{version:03}")
        self.version.setStyleSheet(versionStyle)
    
    def saveBarLayout(self):
        self.saveBar = QtWidgets.QHBoxLayout()
        self.saveBar.addWidget(self.projectName)
        self.saveBar.addWidget(self.fileName)
        self.saveBar.addWidget(self.version)
        self.saveBar.addWidget(self.save)
        self.saveBar.addWidget(self.saveAs)
        #self.setLayout(self.saveBar)


    def fileTreeWidgets(self):

        #style Sheet
        fileTreeStyle = style("fileTreeStyle.qss")
        sceneLogo = hou.ui.createQtIcon("NETWORKS_scene")

        self.files = QtWidgets.QTreeWidget()
        self.files.setColumnCount(3)
        self.header = self.files.header()
        self.header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.files.setColumnWidth(0,180)
        self.files.setHeaderLabels(["Project","Files","Version"])
        #self.files.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        houdiniLogo = hou.ui.createQtIcon("MISC_logo")
        self.files.setStyleSheet(fileTreeStyle)

    def fileTreeLayout(self):
        self.fileTree = QtWidgets.QVBoxLayout()
        #self.fileTree.addWidget(self.files)



    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.layout.addWidget(self.files)   
        self.layout.addLayout(self.saveBar)
        self.setLayout(self.layout)


    # -----------------------------------------------------------------
    # Logic
    # -----------------------------------------------------------------

    def connector(self):
        self.save.clicked.connect(self.saveClicked)
        self.saveAs.clicked.connect(self.saveAsClicked)
        self.settingsCog.clicked.connect(self.settingsDiag)


    def saveClicked(self):
        self.logic.checkJsonExists()
        project = "project"
        file = "file"
        version = 2
        self.logic.saveHipFile(project, file, f"{version:03}")


    def saveAsClicked(self):
        print("not ready, prob gonna change to load")
        

    def settingsDiag(self):
        settings = settingsPannel()
        self.authorUser = "" # this var stores the output of the author feild in the settings pannel
        self.filePathUser = "" #this var stores the output of the projects path of the settings pannel

        def storeAuthor(authorText):
            self.authorUser = authorText

        def storeFilePath(filePathText):
            self.filePathUser = filePathText
        
        settings.authorChanged.connect(storeAuthor)
        settings.filePathChanged.connect(storeFilePath)
        settings.saveButton.clicked.connect(lambda: self.logic.updateJsonSettings("author",self.authorUser))
        settings.saveButton.clicked.connect(lambda: self.logic.updateJsonSettings("homeFolder", self.filePathUser))
        settings.show()

        #self.logic.updateJsonSettings("author",self.authorUser)
        #self.logic.updateJsonSettings("homeFolder", self.filePathUser)

def onCreateInterface():
    return quickProjectUi()

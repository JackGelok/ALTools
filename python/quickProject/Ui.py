import hou
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path
from StyleLoader import style
from .settingsPannel import settingsPannel
from .logic import quickProjectLogic



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

        ############## temp stuff ############
        import json
        project = "test3"
        file = "file"
        jsonPath = Path(f"{hou.getenv('HOUDINI_USER_PREF_DIR')}/ALTools/Projects.json")
        with open(jsonPath, "r") as settFile:
            userdata = json.load(settFile)
            homeDir = Path(userdata["settings"]["homeDir"])
            jsonDir = homeDir / project / f"{project}_Project.json"
        ######################################
    
        self.logic.initProjectJson(project)
        self.logic.addFileToJson(project, file)
        self.logic.incProjectVersion(project, file)

        #self.logic.saveProjectJson(project, "file")
        #version = self.logic.loadProjectJson(jsonDir,"version")
        #self.logic.saveHipFile(project, file, f"{version:03}")


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

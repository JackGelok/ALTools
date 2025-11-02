import hou
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except Exception:
    from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path
from StyleLoader import style
from .settingsPannel import settingsPannel
from .logic import quickProjectLogic
import json
import os




class quickProjectUi(QtWidgets.QDialog):
    projectNameChanged = QtCore.Signal(str)
    fileNameChanged = QtCore.Signal(str)


    def __init__(self):
        super().__init__(hou.qt.mainWindow())
    #non ui logic and globals
        self.logic = quickProjectLogic()
        self.jsonPath = Path(f"{hou.getenv('HOUDINI_USER_PREF_DIR')}/ALTools/Projects.json")
        with open(self.jsonPath, "r") as settFile:
            self.userdata = json.load(settFile)
            self.homeDir = Path(self.userdata["settings"]["homeDir"])
    
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

    #ui dependent logic and glbals
        self.populateFileTree()
        self.connector()
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
        self.load = QtWidgets.QPushButton("Load")
        self.load.setMinimumWidth(70)
        self.load.setMaximumWidth(70)
        self.load.setStyleSheet(buttonsStyle)

        #Project name
        self.projectName = QtWidgets.QLineEdit()
        self.projectName.setStyleSheet(textLineStyle)
        self.projectName.setMaximumWidth(150)
        self.projectName.setPlaceholderText("Project")
        self.projectName.textChanged.connect(self.projectNameChanged.emit)

        #File Name
        self.fileName = QtWidgets.QLineEdit()
        self.fileName.setStyleSheet(textLineStyle)
        self.fileName.setPlaceholderText("Hip File Name")
        self.fileName.textChanged.connect(self.fileNameChanged.emit)

        #Version Counter
        self.version = QtWidgets.QLabel(f"v{0:03}")
        self.version.setStyleSheet(versionStyle)

    def saveBarLayout(self):
        self.saveBar = QtWidgets.QHBoxLayout()
        self.saveBar.addWidget(self.projectName)
        self.saveBar.addWidget(self.fileName)
        self.saveBar.addWidget(self.version)
        self.saveBar.addWidget(self.save)
        self.saveBar.addWidget(self.load)


    def fileTreeWidgets(self):

        #style Sheet
        fileTreeStyle = style("fileTreeStyle.qss")
        fileTreeStyle = self.qssPathCorrector("images", fileTreeStyle)
        


        self.files = QtWidgets.QTreeWidget()
        self.files.setColumnCount(3)
        self.header = self.files.header()
        self.header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.files.setColumnWidth(0,230)
        self.files.setHeaderLabels(["Project","Version","Modified"])
        self.files.setStyleSheet(fileTreeStyle)



    def fileTreeLayout(self):
        self.fileTree = QtWidgets.QVBoxLayout()


    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.layout.addWidget(self.files)   
        self.layout.addLayout(self.saveBar)
        self.setLayout(self.layout)


    # -----------------------------------------------------------------
    # Logic
    # -----------------------------------------------------------------

    def populateFileTree(self):
        """
        Incrementally populate the QTreeWidget with projects, their files, and versions.
        Keeps existing expanded/collapsed state intact.
        """
        # Icons
        houdiniLogo = hou.ui.createQtIcon("MISC_logo")
        sceneLogo = hou.ui.createQtIcon("NETWORKS_scene")
        folderIcon = hou.ui.createQtIcon("BUTTONS_folder")

        # Load homeDir
        homeDir = self.homeDir
        if not homeDir.exists():
            print(f"Home directory does not exist: {homeDir}")
            return

        existingProjects = {self.files.topLevelItem(i).text(0): self.files.topLevelItem(i)
                            for i in range(self.files.topLevelItemCount())}

        # Iterate project folders
        for projectFolder in sorted(homeDir.iterdir()):
            if not projectFolder.is_dir():
                continue

            projectName = projectFolder.name
            projectJson = projectFolder / f"{projectName}_Project.json"
            if not projectJson.exists():
                continue

            # Load project JSON
            with open(projectJson, "r") as file:
                data = json.load(file)

            # Check if project item already exists
            projectItem = existingProjects.get(projectName)
            if not projectItem:
                projectItem = QtWidgets.QTreeWidgetItem(self.files)
                projectItem.setText(0, projectName)
                projectItem.setIcon(0, sceneLogo)
                projectItem.setExpanded(False)

            # Existing file items in project
            existingFiles = {projectItem.child(i).text(0): projectItem.child(i)
                            for i in range(projectItem.childCount())}

            # Add/update files
            filesDict = data.get("Files", {})
            for fileName, fileData in sorted(filesDict.items()):
                fileItem = existingFiles.get(fileName)
                if not fileItem:
                    fileItem = QtWidgets.QTreeWidgetItem(projectItem)
                    fileItem.setText(0, fileName)
                    fileItem.setIcon(0, folderIcon)
                    fileItem.setExpanded(False)

                # Existing versions
                existingVersions = {fileItem.child(i).text(1): fileItem.child(i)
                                    for i in range(fileItem.childCount())}

                versionCount = int(fileData.get("version", "v000").lstrip("v"))
                for v in range(1, versionCount + 1):
                    versionText = f"v{v:03}"
                    if versionText in existingVersions:
                        continue  # version already exists

                    versionName = f"{projectName}_{fileName}_v{v:03}.hip"
                    hipFilePath = Path(projectFolder / versionName)

                    versionItem = QtWidgets.QTreeWidgetItem(fileItem)
                    versionItem.setText(0, fileName)
                    versionItem.setText(1, versionText)

                    if hipFilePath.exists():
                        modifiedDate = QtCore.QDateTime.fromSecsSinceEpoch(int(hipFilePath.stat().st_mtime))
                        versionItem.setText(2, modifiedDate.toString("HH:mm:ss dd/MM/yyyy"))
                    else:
                        versionItem.setText(2, "N/A")

                    versionItem.setIcon(0, houdiniLogo)


    def connector(self):
        self.save.clicked.connect(self.saveClicked)
        self.load.clicked.connect(self.loadFile)
        self.settingsCog.clicked.connect(self.settingsDiag)
        self.files.itemClicked.connect(self.onTreeItemClicked)
        self.files.itemDoubleClicked.connect(self.loadFile)


    def onTreeItemClicked(self, item, column):
        """
        When a tree item is clicked, fill in the Project, File, and Version fields.
        Handles clicks on project, file, or version items correctly.
        """
        parent = item.parent()
        grandparent = parent.parent() if parent else None

        # Version item
        if grandparent:
            projectName = grandparent.text(0)
            fileName = parent.text(0)
            version = item.text(1)
            self.projectName.setText(projectName)
            self.fileName.setText(fileName)
            self.version.setText(version)

        # File item
        elif parent:
            projectName = parent.text(0)
            fileName = item.text(0)
            self.projectName.setText(projectName)
            self.fileName.setText(fileName)

            # Optional: clear version if a file is clicked
            self.version.setText("N/A")

        # Project item
        else:
            projectName = item.text(0)
            self.projectName.setText(projectName)
            self.fileName.setText("")
            self.version.setText("N/A")


    def loadFile(self):
        """
        Loads the currently selected .hip file in Houdini.
        Only works if a version item is selected.
        """
        selectedItems = self.files.selectedItems()
        if not selectedItems:
            hou.ui.displayMessage("No item selected.")
            return

        item = selectedItems[0]
        parent = item.parent()
        grandparent = parent.parent() if parent else None

        if not grandparent:
            return

        # Extract hierarchy
        projectName = grandparent.text(0)
        fileName = parent.text(0)
        version = item.text(1)

        # Build file path
        hipFileName = f"{projectName}_{fileName}_{version}.hip"
        hipFilePath = self.homeDir / projectName / hipFileName

        # Check file existence
        if not hipFilePath.exists():
            hou.ui.displayMessage(f"Hip file not found:\n{hipFilePath}")
            return

        # Load file
        try:
            hou.hipFile.load(str(hipFilePath))
            hou.ui.displayMessage(f"Loaded: {hipFilePath}")
        except Exception as e:
            hou.ui.displayMessage(f"Failed to load file:\n{e}")


    def saveClicked(self):
        project = self.projectName.text()
        file = self.fileName.text()
        jsonDir = self.homeDir / project / f"{project}_Project.json"

        self.logic.initProjectJson(project)
        self.logic.addFileToJson(project, file)
        self.logic.incProjectVersion(project, file)

        V = self.logic.loadProjectJson(jsonDir,("Files",f"{file}","version"))
        self.version.setText(V)
        self.logic.saveHipFile(project, file, V)

        self.populateFileTree()


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


    def qssPathCorrector(self, key, stylesheet):
        qssPath = Path(f"{hou.getenv('HOUDINI_USER_PREF_DIR')}/ALTools/python/{key}")
        qssPathStr = qssPath.as_posix()
        stylesheet = stylesheet.replace(f'{key}/', f'{qssPathStr}/')
        return stylesheet 
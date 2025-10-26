import hou
from PySide6 import QtWidgets, QtCore, QtGui
from StyleLoader import style


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

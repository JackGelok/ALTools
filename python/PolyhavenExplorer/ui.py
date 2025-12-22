import hou
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except Exception:
    from PySide6 import QtWidgets, QtCore, QtGui

class explorerUi(QtWidgets.QDialog):

    def __init__(self):
        super().__init__(hou.qt.mainWindow())

        self.menuBar()
        self.catagoryMenu()
        self.explorer()

        self.mainLayout()



    def menuBar(self):
        
        #assets
        searchIcon = hou.ui.createQtIcon("BUTTONS_search")

        #widgets
        catLabel = QtWidgets.QLabel("Catagories")

        catagoriesMenu = QtWidgets.QComboBox()
        catagoriesMenu.addItems(["test1","test2"])

        searchbar = QtWidgets.QLineEdit()
        searchbar.setPlaceholderText("Search")

        searchbutton = QtWidgets.QPushButton()
        searchbutton.setIcon(searchIcon)

        #layout
        self.menuBarLayout = QtWidgets.QHBoxLayout()

        self.menuBarLayout.addWidget(catLabel)
        self.menuBarLayout.addWidget(catagoriesMenu)
        self.menuBarLayout.addWidget(searchbar)
        self.menuBarLayout.addWidget(searchbutton)



    def catagoryMenu(self):
        pass



    def explorer(self):
        pass



    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.setLayout(self.layout)
        

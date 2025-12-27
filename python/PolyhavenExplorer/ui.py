import hou
from . import PolyhavenAPI
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
        catagories = PolyhavenAPI.list_asset_types()
        print(catagories)

        #widgets
        catLabel = QtWidgets.QLabel("Catagories")

        self.catagoriesMenu = QtWidgets.QComboBox()
        self.catagoriesMenu.addItems(catagories)

        searchbar = QtWidgets.QLineEdit()
        searchbar.setPlaceholderText("Search")

        searchbutton = QtWidgets.QPushButton()
        searchbutton.setIcon(searchIcon)

        #layout
        self.menuBarLayout = QtWidgets.QHBoxLayout()

        self.menuBarLayout.addWidget(catLabel)
        self.menuBarLayout.addWidget(self.catagoriesMenu)
        self.menuBarLayout.addWidget(searchbar)
        self.menuBarLayout.addWidget(searchbutton)



    def catagoryMenu(self):
        #assets

        #widgets

        #layout 
        pass



    def explorer(self):
        pass



    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.setLayout(self.layout)
        

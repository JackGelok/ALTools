import hou
from . import PolyhavenAPI
from . import explorerLogic as logic
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except Exception:
    from PySide6 import QtWidgets, QtCore, QtGui

class explorerUi(QtWidgets.QDialog):

    def __init__(self):
        super().__init__(hou.qt.mainWindow())

        self.logic = logic.logic()

        self.jsonFile = self.logic.loadCache()

        self.menuBar()
        self.catagoryMenu()
        self.explorer()

        self.mainLayout()



    def menuBar(self):

        #assets
        searchIcon = hou.ui.createQtIcon("BUTTONS_search")

        categories = self.jsonFile.get("types", [])
        print(categories)

        #widgets
        catLabel = QtWidgets.QLabel("Catagories")

        self.catagoriesMenu = QtWidgets.QComboBox()
        self.catagoriesMenu.addItems(categories)

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
        #assets
        currentType = self.catagoriesMenu.currentText()

        #widgets
        scrollBar = QtWidgets.QScrollArea()
        scrollBar.setWidgetResizable(True)
        explorerGrid = QtWidgets.QWidget()
        self.explorerLayout = QtWidgets.QGridLayout(explorerGrid)

        #layout 
        pass

    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.setLayout(self.layout)
        




class TestGridUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(hou.qt.mainWindow())
        self.logic = logic.logic()
        self.jsonFile = self.logic.loadCache()
        self.initUI()

    def initUI(self):
        # Main layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Category selector
        self.catCombo = QtWidgets.QComboBox()
        categories = self.jsonFile.get("types", [])
        self.catCombo.addItems(categories)
        self.catCombo.currentTextChanged.connect(self.updateGrid)
        self.layout.addWidget(self.catCombo)

        # Scrollable area for grid
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        self.gridWidget = QtWidgets.QWidget()
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        scrollArea.setWidget(self.gridWidget)
        self.layout.addWidget(scrollArea)

        self.updateGrid(self.catCombo.currentText())

    def updateGrid(self, category):
        # Clear previous items
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get asset names for this category
        assets = self.logic.assetIndex(category)

        # Add them to the grid
        for i, asset_name in enumerate(assets):
            row = i // 4  # 4 columns
            col = i % 3
            widget = QtWidgets.QFrame()
            layout = QtWidgets.QVBoxLayout(widget)
            # Example placeholder for thumbnail
            thumb = QtWidgets.QLabel()
            thumb.setFixedSize(80, 80)
            thumb.setStyleSheet("background-color: #444;")  # gray placeholder
            label = QtWidgets.QLabel(asset_name)
            layout.addWidget(thumb)
            layout.addWidget(label)
            self.gridLayout.addWidget(widget, row, col)

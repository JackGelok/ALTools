import hou
from . import PolyhavenAPI
from . import explorerLogic as logic
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except Exception:
    from PySide6 import QtWidgets, QtCore, QtGui
from flowlayout import FlowLayout

class AssetLoader(QtCore.QThread):
    asset_ready = QtCore.Signal(str)  # Emits asset name when ready
    finished_loading = QtCore.Signal()  # Emits when all assets loaded
    
    def __init__(self, logic_instance, asset_type):
        super().__init__()
        self.logic_instance = logic_instance
        self.asset_type = asset_type
        self._is_running = True
    
    def run(self):
        # Fetch assets in the background thread
        try:
            assets = self.logic_instance.assetIndex(self.asset_type)
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.finished_loading.emit()
            return
        
        # Emit each asset with a small delay
        for asset_name in assets:
            if not self._is_running:
                break
            self.asset_ready.emit(asset_name)
            self.msleep(5)  # Small delay between items
        
        self.finished_loading.emit()
    
    def stop(self):
        self._is_running = False

class explorerUi(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(hou.qt.mainWindow())
        self.logic = logic.logic()
        self.jsonFile = self.logic.loadCache()
        self.loader = None  # Store loader thread
        self.menuBar()
        self.catagoryMenu()
        self.explorer()
        self.mainLayout()
    
    def closeEvent(self, event):
        # Stop loader thread when closing
        if self.loader and self.loader.isRunning():
            self.loader.stop()
            self.loader.wait()
        super().closeEvent(event)
    
    def menuBar(self):
        searchIcon = hou.ui.createQtIcon("BUTTONS_search")
        categories = self.logic.get_asset_types() or ["hdris", "textures", "models"] 
        #print(categories)

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
        
        #connections
        self.catagoriesMenu.currentTextChanged.connect(self.updateExplorer)
    
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
        scrollBar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        explorerGrid = QtWidgets.QWidget()
        self.explorerGridLayout = FlowLayout(explorerGrid)
        #self.explorerGridLayout.setContentsMargins(QtCore.QMargins(10, 10, 10, 10))
        #self.explorerGridLayout.setSpacing(10)
        
        scrollBar.setWidget(explorerGrid)
        #layout 
        self.explorerLayout = QtWidgets.QVBoxLayout()
        self.explorerLayout.addWidget(scrollBar)
        self.updateExplorer(currentType)
    
    def updateExplorer(self, type):
        # Stop any existing loader
        if self.loader and self.loader.isRunning():
            self.loader.stop()
            self.loader.wait()
        
        # Clear existing widgets
        while self.explorerGridLayout.count():
            item = self.explorerGridLayout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        
        # Start loading thread - pass logic instance and type
        self.loader = AssetLoader(self.logic, type)
        self.loader.asset_ready.connect(self.add_asset_widget)
        self.loader.start()
    
    def add_asset_widget(self, asset_name):
        widget = QtWidgets.QFrame()
        widget.setFixedSize(140, 200)  # Fixed size for flow layout
        widget.mousePressEvent = lambda e, name=asset_name: self.onAssetClicked(name)

        
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail
        thumb = QtWidgets.QLabel()
        thumb.setFixedSize(120, 120)
        thumb.setStyleSheet("background-color: #444;")
        thumb.setAlignment(QtCore.Qt.AlignCenter)
        
        # Asset name
        label = QtWidgets.QLabel(self.logic.snakeToSpaced(asset_name))
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        
        layout.addWidget(thumb)
        layout.addWidget(label)
        
        self.explorerGridLayout.addWidget(widget)
    
    def on_loading_finished(self):
        # Optional: do something when all assets are loaded
        print("Finished loading assets")
    
    def mainLayout(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.menuBarLayout)
        self.layout.addLayout(self.explorerLayout)
        self.setLayout(self.layout)

    def onAssetClicked(self, name):
        print(f"{name} was clicked")
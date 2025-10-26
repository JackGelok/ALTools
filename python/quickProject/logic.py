import hou
import json
from pathlib import Path
import os
from quickProject import settingsPannel



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
            settings = settingsPannel()
            settings.show()
        else:
            pass

    def checkJsonExists(self):
        if not os.path.exists(self.jsonPath):
                structure = {
                    "settings": {
                        "author": "",
                        "homeFolder": "",
                        "Style": "Default"
                    }
                }
                
                with open(self.jsonPath, 'w') as file:  
                    json.dump(structure, file, indent=4)
                    print(f"Created new JSON file at: {self.jsonPath}")

    def saveHipFile(self, project, file, version):
        # === get File Path === #
        self.filePath = Path(f"{self.textPath}/{project}/{project}_{file}_v{version}.hip")
        self.filePath.parent.mkdir(parents=True, exist_ok=True)

        # === check for inputs === #
        if not project:
            hou.ui.displayMessage("No Project Was Given",buttons=("Ok",), severity=hou.severityType.Warning)
            return
        if not file:
            hou.ui.displayMessage("No File Name Was Given",buttons=("Ok",), severity=hou.severityType.Warning)
            return

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

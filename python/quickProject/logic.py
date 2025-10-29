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
                        "homeDir": "",
                        "Style": "Default"
                    }
                }

                with open(self.jsonPath, 'w') as file:  
                    json.dump(structure, file, indent=4)
                    print(f"Created new JSON file at: {self.jsonPath}")

    def saveHipFile(self, project, file, version):
        # === get File Path === #
        self.filePath = Path(f"{self.textPath}/{project}/{project}_{file}_{version}.hip")
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


    def saveProjectJson(self, project, filename):
        from datetime import datetime
        now = datetime.now()
        nowFormatted = now.strftime("%d-%m-%Y %H:%M:%S")

        with open(self.jsonPath, "r") as settFile:
            userdata = json.load(settFile)
            author = userdata["settings"]["author"]
            homeDir = Path(userdata["settings"]["homeDir"])
            jsonDir = homeDir / project / f"{project}_Project.json"

        ### === sanity checks === ###
            #== make sure feilds are filled ==#
            if not project:
                hou.ui.displayMessage("Project not specified!",severity=Warning)
                return
            if not filename:
                hou.ui.displayMessage("File name not specified!",severity=Warning)
                return
            if not jsonDir.exists():
                structure = {
                    "ProjectData": {
                        "project": f"{project}",
                        "author": f"{author}",
                        "version": f"v{0:03}",
                        "created": f"{nowFormatted}"
                        },
                    "Files":{
                    }
                    }
                jsonDir.parent.mkdir(parents=True, exist_ok=True)
                with open(jsonDir, "w") as file:
                    json.dump(structure, file, indent=4)



        ### === increment version === ###
        with open(jsonDir,"r") as projFileRead:
            data = json.load(projFileRead)
            version = data["ProjectData"]["version"]

        with open(jsonDir, "w") as projFileWrite:
            version_num = int(version.lstrip("v"))
            newVersion = version_num + 1
            data["ProjectData"]["version"] = f"v{newVersion:03}"
            json.dump(data, projFileWrite, indent=4)
            print(f"{filename} version was updated to v{newVersion:03}")
############################## need to work out kinks in file versioning ###########################


    def loadSettingsJson(self, setting):
        with open(self.jsonPath, "r") as file:
            data = json.load(file)

        print(data["settings"][str(setting)])
        return data["settings"][str(setting)]


    def loadProjectJson(self, projectpath ,value):
        with open(projectpath, "r") as file:
            data = json.load(file)

        print(data["ProjectData"][str(value)])
        return data["ProjectData"][str(value)]

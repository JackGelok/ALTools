import hou
import json
from pathlib import Path
import os
from quickProject import settingsPannel
from PySide6 import QtWidgets
import platform



class quickProjectLogic:
    def __init__(self):
        self.jsonPath = Path(f"{hou.getenv('HOUDINI_USER_PREF_DIR')}/ALTools/Projects.json")
        self.jsonPath.parent.mkdir(parents=True, exist_ok=True) # make sure ALTools folder exists
        self.textPath = "E:/Projects"
        self.startup()
        from datetime import datetime
        nowUnformantted = datetime.now()
        self.now = nowUnformantted.strftime("%d-%m-%Y %H:%M:%S")

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
                    # print(f"Created new JSON file at: {self.jsonPath}")

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
    # print(f"Saved File At: {self.filePath}")

    def updateJsonSettings(self, setting, value):
        if value == "":
            # print("value was blank")
            return

        else:
            with open(self.jsonPath, "r") as file:
                data = json.load(file)

            data["settings"][str(setting)] = value

            with open(self.jsonPath, "w") as file:
                json.dump(data, file, indent=4)

    def initProjectJson(self, project):
        """
        Initialize a new project JSON file for tracking project metadata.
        
        Args:
            project (str): The name of the project to initialize
            
        This function:
        1. Gets the current timestamp for project creation date
        2. Reads user settings from the main settings JSON file
        3. Creates a new project-specific JSON file if it doesn't exist
        4. Sets up initial project metadata including author and creation date
        """

        # Read user settings from main settings file
        with open(self.jsonPath, "r") as settFile:
            userdata = json.load(settFile)
            author = userdata["settings"]["author"]  # Get author from settings
            homeDir = Path(userdata["settings"]["homeDir"])  # Get project home directory
            jsonDir = homeDir / project / f"{project}_Project.json"  # Construct project JSON path

        # Create new project JSON file if it doesn't exist
        if not jsonDir.exists():
            # Define initial project structure
            structure = {
                "ProjectData": {
                    "project": f"{project}",  # Project name
                    "author": f"{author}",    # Project author
                    "created": f"{self.now}"  # Creation timestamp
                    },
                "Files": {  # Empty files section to be populated later
                }
                }
    
            # Create project directory if it doesn't exist
            jsonDir.parent.mkdir(parents=True, exist_ok=True)
            # Write initial project structure to JSON file
            with open(jsonDir, "w") as file:
                json.dump(structure, file, indent=4)
            # print(f"{project} was initilized at {homeDir}\{project}")
        else:
            # print(f"initProjectJson was skiped due to entry {project} already existing")
            pass  # If project JSON already exists, do nothing

    def addFileToJson(self, project, filename):
        with open(self.jsonPath, "r") as settFile:
            userdata = json.load(settFile)
            author = userdata["settings"]["author"]
            homeDir = Path(userdata["settings"]["homeDir"])
            jsonDir = homeDir / project / f"{project}_Project.json"

        with open(jsonDir,"r") as file:
            data = json.load(file)
            
        if filename not in data.get("Files",{}):
            data["Files"][filename] = {
                "version": f"v{0:03}",
                "author": f"{author}",
                "created": f"{self.now}",
                "modified": f"{self.now}"
            }

            with open(jsonDir,"w") as file:
                json.dump(data, file, indent=4)
            # print(f"{filename} was initialized in {project} at {homeDir}\{project}")

        else:
            # print(f"addFileToJson was skiped due to entry {filename} already existing in {project}")
            pass

    def incProjectVersion(self, project, filename):
        """
        This function increments the version of the current file and updates the updated part to the current time
        """

        with open(self.jsonPath, "r") as settFile:
            userdata = json.load(settFile)
            author = userdata["settings"]["author"]
            homeDir = Path(userdata["settings"]["homeDir"])
            jsonDir = homeDir / project / f"{project}_Project.json"

        with open(jsonDir,"r") as file:
            data = json.load(file)
            

        if filename not in data.get("Files",{}):
            # print(f"{filename}, was not found in {project}")
            return
        else:
            with open(jsonDir,"w") as file:
                version = data["Files"][filename]["version"]
                vNum = int(version.lstrip("v"))
                newV = vNum + 1
                data["Files"][filename]["version"] = f"v{newV:03}"
                data["Files"][filename]["modified"] = f"{self.now}"
                json.dump(data,file,indent=4)
                # print(f"{filename} was updated to v{newV:03}")

    def loadSettingsJson(self, setting):
        with open(self.jsonPath, "r") as file:
            data = json.load(file)
        # print(data["settings"][str(setting)])
        return data["settings"][str(setting)]


    def loadProjectJson(self, projectpath , keys):
        """
        Load and return a value from a project JSON file.

        Accepts either a single key (string) or an iterable of keys to traverse
        nested dictionaries. Example usage:

            loadProjectJson(path, 'version')
            loadProjectJson(path, ('Files', 'myfile', 'version'))

        Args:
            projectpath (str | Path): Path to the project JSON file.
            keys (str | Iterable[str]): Key or sequence of keys to traverse.

        Returns:
            The requested value if found, otherwise None.
        """

        projectpath = Path(projectpath)

        # Ensure the project file exists
        if not projectpath.exists():
            hou.ui.displayMessage(f"Project file not found: {projectpath}", buttons=("Ok",), severity=hou.severityType.Warning)
            return None

        # Load JSON from file with basic error handling
        try:
            with open(projectpath, "r") as file:
                data = json.load(file)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to read project file: {e}", buttons=("Ok",), severity=hou.severityType.Warning)
            return None

        # Normalize keys to a tuple to allow uniform traversal
        if isinstance(keys, str):
            keys = (keys,)

        # Traverse nested dictionaries following the provided keys
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                hou.ui.displayMessage(f"Key '{key}' not found while traversing {projectpath}", buttons=("Ok",), severity=hou.severityType.Warning)
                return None

    # Print the result for visibility and return it
    # print(f"got value {current} from {projectpath}")
        return current

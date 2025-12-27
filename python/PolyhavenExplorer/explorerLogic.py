import hou
import json
from pathlib import Path
from . import PolyhavenAPI as papi


class logic:

    def __init__(self):
        self.jsonPath = (Path(hou.getenv("HOUDINI_USER_PREF_DIR")) / "ALTools"/ "polyhaven.json")
        self.jsonPath.parent.mkdir(parents=True, exist_ok=True)

        self.startup()



    def startup(self):
        created = self.checkJsonExists()
        if created:
            print("Polyhaven cache created")
        else:
            print("Polyhaven cache exists")



    def emptyCache(self):
        return {
                "types": {},
                "assets": {
                    "hdris": {},
                    "textures": {},
                    "models": {}
                }
            }



    def checkJsonExists(self):
        """Ensure cache file exists. Returns True if created."""
        if not self.jsonPath.exists():
            structure = {
                "assets": {
                    "hdris": {},
                    "textures": {},
                    "models": {}
                }
            }

            with open(self.jsonPath, "w") as file:
                json.dump(structure, file, indent=4)

            return True
        
        return False



    def assetKeySet(self, assets):
        """
        this gets all the keys stored in the polyhaven database
        
        """
        return {
            "hdris": set(assets.get("hdris", {}).keys()),
            "textures": set(assets.get("textures", {}).keys()),
            "models": set(assets.get("models", {}).keys()),
        }



    def comparePolyhavenAssets(self):
        hdris = papi.list_assets("hdris")
        textures = papi.list_assets("textures")
        models = papi.list_assets("models")

        try:
            with open(self.jsonPath, "r") as file:
                storedData = json.load(file)
        except json.JSONDecodeError:
            print("Cache corrupted — rebuilding")
            storedData = {
                "assets": {
                    "hdris": {},
                    "textures": {},
                    "models": {}
                }
            }

        storedAssets = storedData.get("assets", {})

        newAssets = {
            "hdris": hdris,
            "textures": textures,
            "models": models
        }

        if self.assetKeySet(storedAssets) != self.assetKeySet(newAssets):
            print("Mismatch to source — updating cache")

            storedData["assets"] = newAssets

            with open(self.jsonPath, "w") as file:
                json.dump(storedData, file, indent=4)
        else:
            print("Cache is up to date")



    def assetIndex(self, asset_type=None):
        """
        Returns a list of asset names.
        If asset_type is 'hdris', 'textures', or 'models', returns only that type.
        If None, returns all asset names across all types.
        """
        with open(self.jsonPath, "r") as file:
            storedData = json.load(file)

        assets = storedData.get("assets", {})

        names = []

        if asset_type:
            names = list(assets.get(asset_type, {}).keys())
        else:
            for cat in assets.values():
                names.extend(cat.keys())

        return names


    def assetInfo():
        # name, type, id
        pass

    def assetMetadata():
        # resolution, tags, license, thumbnail
        pass

    def assetSorting():
        # sort + filter helpers
        pass
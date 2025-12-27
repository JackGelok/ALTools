import hou
import json
import requests
from pathlib import Path
from . import PolyhavenAPI as papi


class logic:

    def __init__(self):
        self.jsonPath = Path(hou.getenv("HOUDINI_USER_PREF_DIR")) / "ALTools" / "polyhaven.json"
        self.jsonPath.parent.mkdir(parents=True, exist_ok=True)

        self.startup()

    # --------------------------------------------------
    # Cache helpers
    # --------------------------------------------------

    def emptyCache(self):
        return {
            "online": False,
            "types": [],
            "assets": {
                "hdris": {},
                "textures": {},
                "models": {}
            }
        }


    def loadCache(self):
        try:
            with open(self.jsonPath, "r") as f:
                return json.load(f)
        except Exception:
            print(f"[Polyhaven] Cache invalid or missing, rebuilding")
            return self.emptyCache()

    def saveCache(self, data):
        try:
            with open(self.jsonPath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Polyhaven] Failed to save cache: {e}")

    def checkJsonExists(self):
        if not self.jsonPath.exists():
            self.saveCache(self.emptyCache())
            return True
        return False

    # --------------------------------------------------
    # Startup sync
    # --------------------------------------------------

    def startup(self):
        created = self.checkJsonExists()

        online = self.onlineChecker()

        data = self.loadCache()
        data["online"] = online
        self.saveCache(data)

        if not online:
            print("Polyhaven: offline mode enabled")
            return

        types_changed = self.syncAssetTypes()
        assets_changed = self.comparePolyhavenAssets()

        if created:
            print("Polyhaven cache created")
        elif types_changed or assets_changed:
            print("Polyhaven cache updated")
        else:
            print("Polyhaven cache is up to date")


    # --------------------------------------------------
    # TYPES
    # --------------------------------------------------

    def syncAssetTypes(self):
        """Fetch and store asset types (hdris, textures, models)."""
        data = self.loadCache()

        try:
            types = papi.list_asset_types()
        except Exception as e:
            print("Failed to fetch asset types:", e)
            return False

        if data.get("types") != types:
            data["types"] = types
            self.saveCache(data)
            return True

        return False

    def getAssetTypes(self):
        return self.loadCache().get("types", [])

    # --------------------------------------------------
    # ASSETS
    # --------------------------------------------------

    def assetKeySet(self, assets):
        return {
            "hdris": set(assets.get("hdris", {}).keys()),
            "textures": set(assets.get("textures", {}).keys()),
            "models": set(assets.get("models", {}).keys()),
        }

    def comparePolyhavenAssets(self):
        try:
            hdris = papi.list_assets("hdris")
            textures = papi.list_assets("textures")
            models = papi.list_assets("models")
        except Exception as e:
            print("Failed to fetch asset list:", e)
            return False

        data = self.loadCache()

        stored_assets = data.get("assets", {})

        new_assets = {
            "hdris": hdris,
            "textures": textures,
            "models": models,
        }

        if self.assetKeySet(stored_assets) != self.assetKeySet(new_assets):
            data["assets"] = new_assets
            self.saveCache(data)
            return True

        return False

    # --------------------------------------------------
    # PUBLIC QUERY HELPERS
    # --------------------------------------------------

    def onlineChecker(self, timeout=2.0):
        """
        Checks for if its able to reach polyhaven
        
        :param timeout: Optional, time to see how long it take to ping
        """
        try:
            requests.head("https://api.polyhaven.com", timeout=timeout)
            return True
        except Exception:
            print("Unable to reach Polyhaven API, either its offline or you are not connected to the internet")
            return False

    def assetIndex(self, asset_type=None):
        """
        Returns list of asset IDs.
        """
        data = self.loadCache()
        assets = data.get("assets", {})

        if asset_type:
            return list(assets.get(asset_type, {}).keys())

        out = []
        for group in assets.values():
            out.extend(group.keys())
        return out

    def assetInfo(self, asset_id):
        """
        Returns cached info for one asset if present.
        This gets all of its info from the stored json file
        """
        data = self.loadCache()

        for asset_type, group in data.get("assets", {}).items():
            if asset_id in group:
                return {
                    "id": asset_id,
                    "type": asset_type,
                    "data": group[asset_id],
                }

        return None

    def assetMetadata(self, asset_id):
        """
        Fetch full metadata from PolyHaven API (live).
        Must be online
        """
        try:
            return papi.get_asset_info(asset_id)
        except Exception as e:
            print(f"Failed to fetch metadata for {asset_id}: {e}")
            return None

    # --------------------------------------------------
    # SORTING / FILTERING
    # --------------------------------------------------

    def assetSorting(self, asset_ids, mode="alpha"):
        """
        Sort helpers for UI.
        """
        if mode == "alpha":
            return sorted(asset_ids)

        if mode == "reverse":
            return sorted(asset_ids, reverse=True)

        return asset_ids

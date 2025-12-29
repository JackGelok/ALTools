import hou
import json
import requests
import sqlite3
from pathlib import Path
from . import PolyhavenAPI as papi
from . import assetHelper


class logic:
    def __init__(self):
        self.dbPath = Path(hou.getenv("HOUDINI_USER_PREF_DIR")) / "ALTools" / "polyhaven.db"
        self.dbPath.parent.mkdir(parents=True, exist_ok=True)

        self.assetPath = Path(hou.getenv("HOUDINI_USER_PREF_DIR")) / "ALTools" / "polyhavenAssets"

        self.init_database()
        self.migrate_from_json()
        self.startup()

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    def get_connection(self):
        return sqlite3.connect(str(self.dbPath))

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_types (
                type TEXT PRIMARY KEY
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                description TEXT,
                categories TEXT,
                tags TEXT,
                authors TEXT,
                date_published INTEGER,
                date_taken INTEGER,
                download_count INTEGER,
                thumbnail_url TEXT,
                thumbnail_data BLOB,
                evs_cap INTEGER,
                hdri_type INTEGER,
                whitebalance INTEGER,
                backplates INTEGER,
                coords TEXT,
                info TEXT,
                files_hash TEXT,
                max_resolution TEXT,
                sponsors TEXT,
                dimensions TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_type ON assets(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_name ON assets(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_author ON assets(authors)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_tags ON assets(tags)")

        conn.commit()
        conn.close()

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def get_metadata(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    def set_metadata(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()
        conn.close()

    def is_online(self):
        return self.get_metadata("online", "false") == "true"

    def set_online(self, online):
        self.set_metadata("online", "true" if online else "false")

    # --------------------------------------------------
    # Asset types
    # --------------------------------------------------

    def get_asset_types(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT type FROM asset_types")
        result = [r[0] for r in cursor.fetchall()]
        conn.close()
        return result

    def sync_asset_types(self):
        try:
            types = papi.list_asset_types()
        except Exception as e:
            print("Failed to fetch asset types:", e)
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT type FROM asset_types")
        current = {r[0] for r in cursor.fetchall()}
        incoming = set(types)

        if current != incoming:
            cursor.execute("DELETE FROM asset_types")
            for t in types:
                cursor.execute("INSERT INTO asset_types (type) VALUES (?)", (t,))
            conn.commit()
            changed = True
        else:
            changed = False

        conn.close()
        return changed

    # --------------------------------------------------
    # Asset extraction helpers
    # --------------------------------------------------

    def extract_asset_fields(self, asset_data):
        def join_list(v):
            return ",".join(v) if isinstance(v, list) else ""

        return {
            "name": asset_data.get("name", ""),
            "description": asset_data.get("description", ""),
            "categories": join_list(asset_data.get("categories", [])),
            "tags": join_list(asset_data.get("tags", [])),
            "authors": ",".join(
                f"{k}:{v}" for k, v in asset_data.get("authors", {}).items()
            ),
            "date_published": asset_data.get("date_published"),
            "date_taken": asset_data.get("date_taken"),
            "download_count": asset_data.get("download_count"),
            "thumbnail_url": asset_data.get("thumbnail_url", ""),
            "evs_cap": asset_data.get("evs_cap"),
            "hdri_type": asset_data.get("type"),
            "whitebalance": asset_data.get("whitebalance"),
            "backplates": 1 if asset_data.get("backplates") else 0,
            "coords": ",".join(map(str, asset_data.get("coords", [])))
            if isinstance(asset_data.get("coords"), list)
            else "",
            "info": asset_data.get("info", ""),
            "files_hash": asset_data.get("files_hash", ""),
            "max_resolution": (
                f"{asset_data['max_resolution'][0]}x{asset_data['max_resolution'][1]}"
                if isinstance(asset_data.get("max_resolution"), list)
                else ""
            ),
            "sponsors": ",".join(map(str, asset_data.get("sponsors", []))),
            "dimensions": json.dumps(asset_data.get("dimensions"))
            if asset_data.get("dimensions") is not None
            else "",
        }

    # --------------------------------------------------
    # Sync assets
    # --------------------------------------------------

    def compare_polyhaven_assets(self):
        try:
            assets = {
                "hdris": papi.list_assets("hdris"),
                "textures": papi.list_assets("textures"),
                "models": papi.list_assets("models"),
            }
        except Exception as e:
            print("Failed to fetch asset list:", e)
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM assets")
        current_ids = {r[0] for r in cursor.fetchall()}

        new_ids = set()
        for group in assets.values():
            new_ids.update(group.keys())

        changed = current_ids != new_ids

        if changed:
            cursor.execute("DELETE FROM assets")

            for asset_type, items in assets.items():
                for asset_id, asset_data in items.items():
                    fields = self.extract_asset_fields(asset_data)

                    cursor.execute("""
                        INSERT INTO assets (
                            id, type, name, description, categories, tags,
                            authors, date_published, date_taken, download_count,
                            thumbnail_url, evs_cap, hdri_type, whitebalance,
                            backplates, coords, info, files_hash, max_resolution,
                            sponsors, dimensions
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        asset_id,
                        asset_type,
                        fields["name"],
                        fields["description"],
                        fields["categories"],
                        fields["tags"],
                        fields["authors"],
                        fields["date_published"],
                        fields["date_taken"],
                        fields["download_count"],
                        fields["thumbnail_url"],
                        fields["evs_cap"],
                        fields["hdri_type"],
                        fields["whitebalance"],
                        fields["backplates"],
                        fields["coords"],
                        fields["info"],
                        fields["files_hash"],
                        fields["max_resolution"],
                        fields["sponsors"],
                        fields["dimensions"],
                    ))

            conn.commit()

        conn.close()
        return changed

    # --------------------------------------------------
    # Thumbnails
    # --------------------------------------------------

    def save_thumbnail(self, asset_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE assets SET thumbnail_data=? WHERE id=?",
            (data, asset_id),
        )
        conn.commit()
        conn.close()

    def get_thumbnail(self, asset_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT thumbnail_data FROM assets WHERE id=?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def download_and_save_thumbnail(self, asset_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT thumbnail_url FROM assets WHERE id=?", (asset_id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            return False

        try:
            r = requests.get(row[0], timeout=10)
            r.raise_for_status()
            self.save_thumbnail(asset_id, r.content)
            return True
        except Exception as e:
            print(f"Thumbnail failed for {asset_id}: {e}")
            return False

    def cache_all_thumbnails(self, force=False):
        """
        Downloads and stores thumbnail URLs + local files for all assets.
        Intended to be run once at startup.
        """

        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, thumbnail_url FROM assets")
        rows = cur.fetchall()

        thumb_dir = Path(self.cache_dir) / "thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)

        updated = 0

        for asset_id, thumb_url in rows:
            if thumb_url and not force:
                continue

            # ask PolyHaven for asset info
            try:
                data = self.api.get_asset(asset_id)
            except Exception:
                continue

            thumb = data.get("thumbnail")
            if not thumb:
                continue

            # save URL
            cur.execute(
                "UPDATE assets SET thumbnail_url=? WHERE id=?",
                (thumb, asset_id),
            )

            # download file
            try:
                response = requests.get(thumb, timeout=10)
                if response.ok:
                    out_path = thumb_dir / f"{asset_id}.jpg"
                    with open(out_path, "wb") as f:
                        f.write(response.content)
            except Exception:
                pass

            updated += 1

        conn.commit()
        conn.close()

        return updated


    # --------------------------------------------------
    # Query helpers
    # --------------------------------------------------

    def assetIndex(self, asset_type=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        if asset_type:
            cursor.execute("SELECT id FROM assets WHERE type=? ORDER BY name", (asset_type,))
        else:
            cursor.execute("SELECT id FROM assets ORDER BY name")

        ids = [r[0] for r in cursor.fetchall()]
        conn.close()
        return ids

    def search_assets(self, query, asset_type=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        pattern = f"%{query}%"

        if asset_type:
            cursor.execute("""
                SELECT id FROM assets
                WHERE type=? AND (name LIKE ? OR tags LIKE ? OR authors LIKE ?)
            """, (asset_type, pattern, pattern, pattern))
        else:
            cursor.execute("""
                SELECT id FROM assets
                WHERE name LIKE ? OR tags LIKE ? OR authors LIKE ?
            """, (pattern, pattern, pattern))

        ids = [r[0] for r in cursor.fetchall()]
        conn.close()
        return ids

    # --------------------------------------------------
    # Startup
    # --------------------------------------------------

    def checkAssetFolderExists(self):
        self.assetPath.mkdir(parents=True, exist_ok=True)
        (self.assetPath / "thumbnails").mkdir(exist_ok=True)

    def onlineChecker(self, timeout=2.0):
        try:
            requests.head("https://api.polyhaven.com", timeout=timeout)
            return True
        except Exception:
            return False

    def startup(self):
        self.checkAssetFolderExists()
        online = self.onlineChecker()
        self.set_online(online)

        if not online:
            print("Polyhaven: offline mode")
            return

        changed = self.sync_asset_types()
        changed |= self.compare_polyhaven_assets()

        updated = self.cache_all_thumbnails()
        print(f"Cached {updated} thumbnails")

        if changed:
            print("Polyhaven cache updated")
        else:
            print("Polyhaven cache up to date")


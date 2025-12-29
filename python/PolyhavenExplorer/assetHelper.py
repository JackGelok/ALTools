import json
from .explorerLogic import logic


class AssetHelper:
    def __init__(self, logic_instance=None):
        self.logic = logic_instance or logic()

    # -----------------------------
    # Core field access
    # -----------------------------

    def get_field(self, asset_id, field):
        conn = self.logic.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {field} FROM assets WHERE id=?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_multiple_fields(self, asset_id, fields):
        conn = self.logic.get_connection()
        cursor = conn.cursor()

        safe = ", ".join(fields)
        cursor.execute(f"SELECT {safe} FROM assets WHERE id=?", (asset_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(zip(fields, row)) if row else {}

    # -----------------------------
    # Simple getters
    # -----------------------------

    def get_name(self, asset_id):
        return self.get_field(asset_id, "name") or ""

    def get_description(self, asset_id):
        return self.get_field(asset_id, "description") or ""

    def get_type(self, asset_id):
        return self.get_field(asset_id, "type") or ""

    def get_thumbnail_url(self, asset_id):
        return self.get_field(asset_id, "thumbnail_url") or ""

    def get_download_count(self, asset_id):
        return self.get_field(asset_id, "download_count") or 0

    def get_date_published(self, asset_id):
        return self.get_field(asset_id, "date_published")

    def get_date_taken(self, asset_id):
        return self.get_field(asset_id, "date_taken")

    def get_whitebalance(self, asset_id):
        return self.get_field(asset_id, "whitebalance")

    def get_evs_cap(self, asset_id):
        return self.get_field(asset_id, "evs_cap")

    def get_files_hash(self, asset_id):
        return self.get_field(asset_id, "files_hash") or ""

    # -----------------------------
    # Parsed fields
    # -----------------------------

    def get_categories(self, asset_id):
        v = self.get_field(asset_id, "categories")
        return v.split(",") if v else []

    def get_tags(self, asset_id):
        v = self.get_field(asset_id, "tags")
        return v.split(",") if v else []

    def get_authors(self, asset_id):
        raw = self.get_field(asset_id, "authors")
        if not raw:
            return {}
        out = {}
        for pair in raw.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                out[k] = v
        return out

    def get_author_names(self, asset_id):
        return list(self.get_authors(asset_id).keys())

    def has_backplates(self, asset_id):
        return bool(self.get_field(asset_id, "backplates"))

    def get_coords(self, asset_id):
        raw = self.get_field(asset_id, "coords")
        if raw and "," in raw:
            try:
                a, b = raw.split(",")
                return [float(a), float(b)]
            except:
                return None
        return None

    def get_max_resolution(self, asset_id):
        raw = self.get_field(asset_id, "max_resolution")
        if raw and "x" in raw:
            try:
                w, h = raw.split("x")
                return [int(w), int(h)]
            except:
                return None
        return None

    def get_sponsors(self, asset_id):
        raw = self.get_field(asset_id, "sponsors")
        return raw.split(",") if raw else []

    def get_dimensions(self, asset_id):
        raw = self.get_field(asset_id, "dimensions")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except:
            return None

    # -----------------------------
    # Batch helpers
    # -----------------------------

    def get_names_batch(self, asset_ids):
        conn = self.logic.get_connection()
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(asset_ids))
        cursor.execute(
            f"SELECT id, name FROM assets WHERE id IN ({placeholders})",
            asset_ids,
        )

        result = {r[0]: r[1] for r in cursor.fetchall()}
        conn.close()
        return result

    def get_thumbnails_batch(self, asset_ids):
        conn = self.logic.get_connection()
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(asset_ids))
        cursor.execute(
            f"SELECT id, thumbnail_url FROM assets WHERE id IN ({placeholders})",
            asset_ids,
        )

        result = {r[0]: r[1] for r in cursor.fetchall()}
        conn.close()
        return result

    def get_basic_info_batch(self, asset_ids):
        conn = self.logic.get_connection()
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(asset_ids))
        cursor.execute(
            f"""
            SELECT id, name, thumbnail_url, download_count
            FROM assets WHERE id IN ({placeholders})
            """,
            asset_ids,
        )

        out = {}
        for row in cursor.fetchall():
            out[row[0]] = {
                "name": row[1],
                "thumbnail_url": row[2],
                "download_count": row[3],
            }

        conn.close()
        return out

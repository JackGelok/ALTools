import requests
import os

BASE_URL = "https://api.polyhaven.com"
HEADERS = {
    "User-Agent": "PolyhevenExplorerHoudini/0.1 (jackmgelok@gmail.com)"
}

def list_asset_types():
    """Get the available asset types (hdris, textures, models)."""
    url = f"{BASE_URL}/types"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def list_assets(asset_type="all", categories=None):
    """
    List assets.
    - asset_type: 'hdris', 'textures', 'models' or 'all'
    - categories: comma-separated string of categories
    """
    params = {}
    if asset_type:
        params["type"] = asset_type
    if categories:
        params["categories"] = categories

    url = f"{BASE_URL}/assets"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_asset_info(asset_id):
    """Get metadata for a specific asset by ID."""
    url = f"{BASE_URL}/info/{asset_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_asset_files(asset_id):
    """
    Get the file structure for an asset.
    This returns URLs for files of that asset.
    """
    url = f"{BASE_URL}/files/{asset_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def download_file(file_url, save_path):
    """Download a file from a URL to a local path."""
    print(f"Downloading: {file_url}")
    r = requests.get(file_url, headers=HEADERS)
    r.raise_for_status()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(r.content)

    print(f"Saved to: {save_path}")


def list_categories(asset_type: str):
    """
    List categories for a given asset type.
    
    asset_type must be one of:
    - 'hdris'
    - 'textures'
    - 'models'
    """
    url = f"{BASE_URL}/categories/{asset_type}"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    # 1. List all types
    types = list_asset_types()
    print("Asset types:", types)

    # 2. List some assets
    assets = list_assets(asset_type="hdris")
    print("HDRIs found:", len(assets))
    for i, (aid, meta) in enumerate(assets.items()):
        print(f"{i+1:02d}. ID: {aid}, Name: {meta['name']}")
        if i >= 4:
            break

    # 3. Pick an asset ID (example: first one)
    example_id = list(assets.keys())[0]
    print("\nFetching info for:", example_id)

    info = get_asset_info(example_id)
    print("Asset info:", info)

    # 4. Get files for that asset
    files = get_asset_files(example_id)
    print("Files info:", files)

    # 5. Optional: Download a specific file from the structure
    # (Find a real URL in the nested `files` dict and pass it in)
    # e.g., files["hdri"]["hdri"]["16384x8192"]["file"]["url"]

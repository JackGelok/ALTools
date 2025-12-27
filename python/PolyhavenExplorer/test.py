import hou
from . import PolyhavenAPI as papi

def testing():
    test = papi.list_asset_types()
    print(test)
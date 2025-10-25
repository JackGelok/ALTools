from pathlib import Path
import hou 

def style(name, baseDir=None):
    if baseDir is None:
        baseDir = Path(__file__).parent
    
    stylePath = Path(baseDir/"Styles"/name)

    if stylePath.exists():
        with open(stylePath) as file:
            data = file.read()
            #return file.read
            file.close()
        return data
    
    else:
        hou.ui.displayMessage(f"Style not found at {stylePath}")
        #return ""
    

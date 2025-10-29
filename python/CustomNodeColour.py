import hou

def setNodeColour():
    nodes = hou.selectedNodes()

    ### check for if nodes are selected ###
    if not nodes:
        hou.ui.displayMessage("No nodes Selected")
        return
    else:
        pass
    
    ### select and change node colour ###
    color = hou.ui.selectColor(initial_color=hou.Color((1.0, 1.0, 1.0)))
    if color is not None:
        for node in hou.selectedNodes():
            node.setColor(color)
        else:
            return




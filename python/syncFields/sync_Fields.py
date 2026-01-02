import hou

def sync(kwargs):
    """
    Creates relative references to all sibling fields    
    """
    parm = kwargs['parms'][0]
    parm_tuple = parm.tuple()

    current_index = list(parm_tuple).index(parm)
    
    all_parms = list(parm_tuple)
    
    
    for i, target_parm in enumerate(all_parms):
        if i != current_index:  # Skip the source parameter itself
            try:
                relative_expr = f'ch("{parm.name()}")'
                target_parm.setExpression(relative_expr)
                
            except hou.OperationFailed as e:
                hou.ui.displayMessage(f"Failed to set reference on {target_parm.name()}: {str(e)}")
    
    #hou.ui.displayMessage(f"Synced {parm.name()} to {len(all_parms)-1} sibling parameter(s)")

def checkSyncable(kwargs):
    """
    Determines if the sync option should be available
    Returns True if the parameter is part of a tuple with multiple components
    """
    parm = kwargs['parms'][0]
    parm_tuple = parm.tuple()
    
    return len(parm_tuple) > 1
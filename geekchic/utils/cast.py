FALSE_STRINGS = ("0", "false", "[]", "{}", "()", "None", "no")

def boolean(obj):
    """
    A helper method for converting POST and JSON data
    to an expected Boolean object (Python bool). 

    We expect that the following are false:
        
        0
        False
        []
        {}
        ()
        epsilon
        None

    Therefore case insensitive string representations
    of them should also be false. If obj is a string,
    we check for these representations, otherwise,
    we simply revert to bool()
    """
    if isinstance(obj, str) or isinstance(obj, unicode):
        obj = obj.lower() # Case Insensitivity
        if obj in FALSE_STRINGS:
            return False
    return bool(obj)

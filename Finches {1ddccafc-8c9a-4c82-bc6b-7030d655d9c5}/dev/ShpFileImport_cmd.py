import rhinoscript.userinterface
import rhinoscript.geometry

__commandname__ = "ShpFileImport"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
    print "Hello", __commandname__
    # get a point
    point = rhinoscript.userinterface.GetPoint()
    if( point != None ):
    rhinoscript.geometry.AddPoint(point)

    # you can optionally return a value from this function
    # to signify command result. Return values that make
    # sense are
    #   0 == success
    #   1 == cancel
    # If this function does not return a value, success is assumed
    return 0

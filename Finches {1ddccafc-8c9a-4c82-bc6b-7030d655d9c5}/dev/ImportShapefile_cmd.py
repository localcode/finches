import os
import sys
from pprint import pprint

import rhinoscript.userinterface as UI
import rhinoscript.geometry
from scriptcontext import doc

from ShpToRhino import ShpFileToRhino

__commandname__ = "ImportShapefile"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"



def RunCommand( is_interactive ):
  print "Hello", __commandname__
  paths = UI.OpenFileNames(
    'Select the ".shp" files you want to import to Rhino',
    "ESRI Shapefiles (*.shp)|*.shp||",
  )
  paths = list(paths)
  for path in paths:
      if checkPath(path):
          geoms = ShpFileToRhino(path)
          for geom in geoms:
              doc.Objects.Add(geom)
  
  pprint(paths)
  
  # you can optionally return a value from this function
  # to signify command result. Return values that make
  # sense are
  #   0 == success
  #   1 == cancel
  # If this function does not return a value, success is assumed
  return 0

def checkPath(pth):
    root, ext = os.path.splitext(pth)
    exists = os.path.exists(pth)
    if exists:
        hasProj = os.path.exists(root + ".prj")
        hasDbf = os.path.exists(root + ".dbf")
        if hasProj and hasDbf:
            return True
    return False
       
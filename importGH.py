#import Rhino
import os
import sys

# edit sys.path
package = '~/Dropbox/localcode/rhinotools'
expanded = os.path.abspath(os.path.expanduser(package))
if expanded not in sys.path:
    sys.path.append(expanded)

decom = [
    'Shp',
    'ShpFeature',
    'ShpToRhino',
    ]
for m in decom:
    if m in sys.modules:
        del sys.modules[m]

# get the module
import Shp
import ShpFeature
import ShpToRhino


if read:
    if shapefile:
        if not os.path.exists(shapefile):
            print 'The shapefile you gave me does not exist.\nDouble check the path: "%s"' % shapefile
        # import stuff
        out = ShpToRhino.ShpFileToRhino( shapefile, moveToCenter )
        print out
    else:
        print 'no shapefile supplied'



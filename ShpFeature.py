
class ShpFeature(object):
    '''
    This is a base class for each record in a shapefile.
    each record corresponds to one row in the shapefile's dbf table.
    To clarify the distinction between a feature and a record:
    the record is the feature + the dbf data associated with the feature
    the feature is shape (or multi-shape)
    In this class, I attach the dbf data for each record to it's feature.
    '''

    def __init__(self, shpFile, recordNumber):
        self.shpFile = shpFile
        self.recordNumber = recordNumber
        self.shapeType = shpFile.shapeType
        self.dbfData = self.readDbfData()

    def readDbfData(self):
        db = self.shpFile.dbfTable
        dbfData = {}
        for i in range(len(db[0])): # for each column
                dbfData[db[0][i]] = db[self.recordNumber + 2][i]
        return dbfData

    def make3D(self, zVals=None):
        """
        This method will take a list of z values and use them to create a new
        attribute called points3D, which contains 3d points. ESRI shapefiles
        place z values in a separate list form x and y values for each point,
        so this essentially integrates those values to make full 3d points.
        If the number of z values does not match the number of points,
        then this method will not work.
        This method will overwrite the points3d attribute if it already exists.
        """
        # if there's not enough z values for the number of points
        # or not enough points for the number of z values
        if not zVals:
            zVals = [0 for i in range(self.numPoints)]
        if len(zVals) != self.numPoints:
            print "The number of Z values does not correspond to the number of points."
            return
        # clear points3D
        self.points3D = []
        for i in range(len(zVals)):
            z = zVals[i]
            x = self.points[i][0]
            y = self.points[i][1]
            point3d = (x,y,z)
            self.points3D.append(point3d)

    def chopParts(self, partlist, pointlist):
        if type(partlist) == tuple:
            indexSpread = list(partlist)
        elif type(partlist) == list:
            indexSpread = partlist
        else:
            indexSpread = [partlist]
        indexSpread.append(len(pointlist))
        chunks = []
        for i in range(len(indexSpread) - 1):
            chunks.append(pointlist[indexSpread[i]:indexSpread[i+1]])
        return chunks



class ShpPoint(ShpFeature):

    def __init__(self, ShpFile, recordNumber):
        ShpFeature.__init__(self, ShpFile, recordNumber)
        self.parts = [0]
        self.numParts = 1
        self.numPoints = 1
        self.points = [self.shpFile._readPoint()]
        self.x = self.points[0][0]
        self.y = self.points[0][1]
        self.make3D()

class ShpPointM(ShpPoint):
    def __init__(self,ShpFile, recordNumber):

        ShpPoint.__init__(self, ShpFile, recordNumber)

        self.m = self.shpFile._readZ()
        self.make3D()

class ShpPointZ(ShpPoint):
    def __init__(self,ShpFile, recordNumber):

        ShpPoint.__init__(self, ShpFile, recordNumber)

        self.z = self.shpFile._readZ()
        self.m = self.shpFile._readZ()
        self.make3D([self.z])

class ShpMultiPoint(ShpFeature):

    def __init__(self,ShpFile, recordNumber):

        ShpFeature.__init__(self, ShpFile, recordNumber)
        self.parts[0]
        self.numParts = 1
        self.boundingBox = self.shpFile._readBoundingBox()
        self.numPoints = self.shpFile._readNumPoints()
        self.points = self.shpFile._readPoints(self.numPoints)
        self.make3D()

class ShpMultiPointM(ShpMultiPoint):

    def __init__(self,ShpFile, recordNumber):

        ShpMultiPoint.__init__(self, ShpFile, recordNumber)
        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D()

class ShpMultiPointZ(ShpMultiPoint):

    def __init__(self,ShpFile, recordNumber):

        ShpMultiPoint.__init__(self, ShpFile, recordNumber)
        self.zBounds = self.shpFile._readZBounds()
        self.zArray = self.shpFile._readZArray(self.numPoints)
        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D(self.zArray)

class ShpPolyLine(ShpFeature):

    def __init__(self,ShpFile, recordNumber):

        ShpFeature.__init__(self, ShpFile, recordNumber)

        self.boundingBox = self.shpFile._readBoundingBox()
        self.numParts = self.shpFile._readNumParts()
        self.numPoints = self.shpFile._readNumPoints()
        self.parts = self.shpFile._readParts(self.numParts)
        self.points = self.shpFile._readPoints(self.numPoints)
        self.make3D()

class ShpPolyLineM(ShpPolyLine):

    def __init__(self,ShpFile, recordNumber):

        ShpPolyLine.__init__(self, ShpFile, recordNumber)

        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D()

class ShpPolyLineZ(ShpPolyLine):

    def __init__(self,ShpFile, recordNumber):

        ShpPolyLine.__init__(self, ShpFile, recordNumber)

        self.zBounds = self.shpFile._readZBounds()
        self.zArray = self.shpFile._readZArray(self.numPoints)
        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D(self.zArray)

class ShpPolygon(ShpFeature):

    def __init__(self,ShpFile, recordNumber):

        ShpFeature.__init__(self, ShpFile, recordNumber)

        self.boundingBox = self.shpFile._readBoundingBox()
        self.numParts = self.shpFile._readNumParts()
        self.numPoints = self.shpFile._readNumPoints()
        self.parts = self.shpFile._readParts(self.numParts)
        self.points = self.shpFile._readPoints(self.numPoints)
        self.make3D()

class ShpPolygonM(ShpPolygon):

    def __init__(self,ShpFile, recordNumber):

        ShpPolygon.__init__(self, ShpFile, recordNumber)

        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D()

class ShpPolygonZ(ShpPolygon):

    def __init__(self,ShpFile, recordNumber):

        ShpPolygon.__init__(self, ShpFile, recordNumber)

        self.zBounds = self.shpFile._readZBounds()
        self.zArray = self.shpFile._readZArray(self.numPoints)
        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D(self.zArray)

class ShpMultiPatch(ShpFeature):

    def __init__(self, ShpFile, recordNumber):

        ShpFeature.__init__(self, ShpFile, recordNumber)

        self.boundingBox = self.shpFile._readBoundingBox()
        self.numParts = self.shpFile._readNumParts()
        self.numPoints = self.shpFile._readNumPoints()
        self.parts = self.shpFile._readParts(self.numParts)
        self.partTypes = self.shpFile._readParts(self.numParts)
        self.points = self.shpFile._readPoints(self.numPoints)
        self.zBounds = self.shpFile._readZBounds()
        self.zArray = self.shpFile._readZArray(self.numPoints)
        self.mBounds = self.shpFile._readZBounds()
        self.mArray = self.shpFile._readZArray(self.numPoints)
        self.make3D(self.zArray)
        #self.points = [self.shpFile._readPoint()]



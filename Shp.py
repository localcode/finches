'''
Created on Oct 22, 2010

@author: Benjamin Golder

This module was inspired by shpUtils by
Zachary Forest Johnson
which was later edited by
Michael Geary
'''
import dbfUtils
from struct import unpack
from ShpFeature import *

def readAndUnpack(type, data):
    if data=='': return data
    return unpack(type, data)[0]

shapeTypeDict = {
                 0:'Null Shape',
                 1:'Point',
                 3:'PolyLine',
                 5:'Polygon',
                 8:'MultiPoint',
                 11:'PointZ',
                 13:'PolyLineZ',
                 15:'PolygonZ',
                 18:'MultiPointZ',
                 21:'PointM',
                 23:'PolyLineM',
                 25:'PolygonM',
                 28:'MultiPointM',
                 31:'MultiPatch'
                 }

classTypeDict = {
                'Point':ShpPoint,
                'PointM':ShpPointM,
                'PointZ':ShpPointZ,
                'MultiPoint':ShpMultiPoint,
                'MultiPointM':ShpMultiPointM,
                'MultiPointZ':ShpMultiPointZ,
                'PolyLine':ShpPolyLine,
                'PolyLineM':ShpPolyLineM,
                'PolyLineZ':ShpPolyLineZ,
                'Polygon':ShpPolygon,
                'PolygonM':ShpPolygonM,
                'PolygonZ':ShpPolygonZ,
                'MultiPatch':ShpMultiPatch
                }


class ShpFile(object):
    '''
    This class is instantiated using the file path to a shapefile (must contain the .shp file extension), and as soon as it is instantiated, it reads the entire shapefile.
    Once instantiated, it contains objects for each feature based on shape type (the objects are accessible using the
    .records attribute), and allows access to the shapefile data at multiple levels.
    '''

    def __init__(self,filePath):
        self.filePath = filePath
        self.proj = self._readProjText()
        self.dbfTable = self._readDbfTable()
        self.f = open(self.filePath, 'rb')
        header = self._readFileHeader()
        self.shapeType = header[0]
        self.boundingBox = header[1]
        self.records = self._readRecords()
        self.f.close()

    def _readBoundingBox(self):
        xMin = readAndUnpack('d', self.f.read(8))
        yMin = readAndUnpack('d', self.f.read(8))
        xMax = readAndUnpack('d', self.f.read(8))
        yMax = readAndUnpack('d', self.f.read(8))
        bbox = (xMin, yMin, xMax, yMax)
        return bbox

    def _readProjText(self):
        projPath = self.filePath[0:-4] + '.prj'
        f = open(projPath, 'r')
        s = f.read()
        return s


    def _readFileHeader(self):
        self.f.seek(32)
        shapeKey =  readAndUnpack('i', self.f.read(4))
        shapeType = shapeTypeDict[shapeKey]
        boundingBox = self._readBoundingBox()
        return (shapeType, boundingBox)

    def _readPoint(self):
        x = readAndUnpack('d', self.f.read(8))
        y = readAndUnpack('d', self.f.read(8))
        return (x,y)

    def _readNumParts(self):
        return readAndUnpack('i', self.f.read(4))

    def _readNumPoints(self):
        return readAndUnpack('i', self.f.read(4))

    def _readParts(self, numParts):
        partIndices = []
        for i in range(numParts):
            partIndex = readAndUnpack('i', self.f.read(4))
            partIndices.append(partIndex)
        return partIndices

    def _readPoints(self, numPoints):
        points = []
        # I removed a short chunk of code here
        # that was used to remove any two identical
        # consecutive points. Such a check is only relevant if
        # each part is being checked separately, otherwise
        # a part that begins where the other left off would be
        # messed up.
        for i in range(numPoints):
            point = self._readPoint()
            points.append(point)
        return points

    def _readZ(self):
        z = readAndUnpack('d', self.f.read(8))
        return z

    def _readZBounds(self):
        zMin = self._readZ()
        zMax = self._readZ()
        return (zMin,zMax)

    def _readZArray(self, numPoints):
        zArray = []
        for i in range(numPoints):
            z = self._readZ()
            zArray.append(z)
        return zArray


    def setZfield(self, fieldKey=None, zValue=0.0):
        # this method will erase any existing
        # z data of the geometry
        # and will replace it with values
        # from the field designated
        # by the fieldKey
        zValue = 0.0
        for record in self.records:
            if fieldKey != None:
                try:
                    zValue = float(record.dbfData[fieldKey])
                except:
                    print 'There is no field by that name in the table'
                    return
            zArray = []
            for each in range(record.numPoints):
                zArray.append(zValue)
            record.make3D(zArray)

    def _readDbfTable(self):
        dbfFile = self.filePath[0:-4] + '.dbf'
        dbf = open(dbfFile, 'rb')
        db = list(dbfUtils.dbfreader(dbf))
        dbf.close()
        return db

    def _readRecords(self):
        records = []
        self.f.seek(100)
        iterator = 0
        while True:
            record = self._readFeature(iterator)
            if record == False:
                    break
            records.append(record)
            iterator += 1
        return records

    def _readFeature(self, iterator):
        # the next 12 bytes are simply passed over, though they contain:
        # a record number: which doesn't seem to correspond to the dbf
        # a content length integer
        # a shapeType integer, which is never different form the shapeType of the file
        read = self.f.read(12)
        if read == '':
                # signifies end of shapefile
                return False
        else:
            # get shapeType and creates appropriate feature
            feature = classTypeDict[self.shapeType](self,iterator)
            return feature

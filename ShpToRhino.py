from Shp import ShpFile
try:
    import Rhino
except:
    pass



def addUserStrings(feature, geom):
    data = feature.dbfData
    for k in data:
        try:
            geom.UserDictionary.Set(k, data[k])
        except:
            pass
    return geom

def tVect(geom, vector):
    geom.Translate(vector)
    geom.SetUserString('TranslationVector', str(vector) )
    return geom

def transVectorFromBBox(shpFile):
    """Uses the bounding box of a shapefile to make a vector moving Rhino geometry to the origin. The translation vector
    can also be stored as a user string the Rhino geometry, for later conversion back into geospatial data."""
    b = shpFile.boundingBox
    originalCenterPoint = ((b[0]+b[2])/2, (b[1]+b[3])/2, 0.0)
    translationVectr = Rhino.Geometry.Vector3d((b[0]+b[2])/-2.0, (b[1]+b[3])/-2.0, 0.0)
    return translationVectr

def chop(indices, someList):
    for i in range(len(indices)-1):
        idx1, idx2 = indices[i], indices[i+1]
        yield someList[idx1:idx2]

def chopPoints( feature ):
    if feature.numParts > 1:
        return [p for p in chop(feature.parts, feature.points3D)]
    else:
        return [feature.points3D]

def shpToPoints( feature, translationVector=None ):
    points = [addUserStrings(feature, Rhino.Geometry.Point3d(*p)) for p in feature.points3D]
    if translationVector:
        points = [p.Add(p, translationVector) for p in points]
    return points

def shpToCurve( feature, translationVector=None, degree=1):
    parts = chopPoints( feature )
    crvs = []
    for part in parts:
        points = []
        for pt in part:
            rhPoint = Rhino.Geometry.Point3d( *pt )
            points.append( rhPoint )
        crv = Rhino.Geometry.Curve.CreateControlPointCurve( points, degree )
        if translationVector:
            crv = tVect(crv, translationVector )
        crvs.append( addUserStrings(feature, crv) )
    return crvs

def shpToMesh( multiPatchFeature, translationVector=None ):
    m = multiPatchFeature
    parts = chopPoints(m)
    mesh = Rhino.Geometry.Mesh()
    for i, points in enumerate(parts):
        if m.partTypes[i] == 0: # it's a a triangle strip
            submesh = Rhino.Geometry.Mesh()
            for j, pt in enumerate(points): # build vertices
                rhPoint = Rhino.Geometry.Point3d(*pt)
                submesh.Vertices.Add(rhPoint)
            for n in range(len(points)-1):
                submesh.Faces.AddFace(n, n +1, n +2 )
            submesh.Normals.ComputeNormals()
            submesh.Compact()
            mesh.Append(submesh)
        else: # it's some other geometry
            return 'This geometry type is not yet supported, sorry.'
    mesh.UnifyNormals()
    mesh.Normals.ComputeNormals()
    mesh.Compact() # mesh all fresh and ready!
    if translationVector:
        mesh = tVect( mesh, translationVector)
    return [ addUserStrings(m, mesh) ]



translationDict = {
                   'Point':shpToPoints,
                   'Polygon':shpToCurve,
                   'PolyLine':shpToCurve,
                   'PolyLineZ':shpToCurve,
                   'PolygonZ':shpToCurve,
                   'MultiPatch':shpToMesh
                   }


def ShpFileToRhino( filepath, zero=True, tVect=None ):
    shpfile = ShpFile( filepath )
    if zero:
        tVect = transVectorFromBBox( shpfile )
    records = shpfile.records
    geoms = []
    for r in records:
        geoms.extend( translationDict[ shpfile.shapeType ]( r, tVect ) )
    return geoms

def run():
    import os
    path = [
        'multipatch_Project.shp',
        'polylineZ_Project.shp',
        'line_Project.shp',
        'rectangle_Project.shp',
        'lotsWGS84UTMZ10.shp',
    ]
    folder = 'testdata'
    fpath = os.path.join(folder, path[0])
    import scriptcontext
    geom = ShpFileToRhino( fpath )
    for g in geom:
        scriptcontext.doc.Objects.AddMesh( g )


if __name__=='__main__':
    #import profile
    #profile.run('run()')
    run()


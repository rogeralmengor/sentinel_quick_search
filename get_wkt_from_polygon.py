from osgeo import ogr
from shapely.wkt import loads
from shapely.geometry import LineString
import sys 

if len(sys.argv) < 2: 
    print("Enter complete path to shapefile")
    sys.exit(1)

path = sys.argv[1] 

polygon = ogr.Open(path)

layer = polygon.GetLayer()

geoms = []

for feature in layer:
    geom = feature.GetGeometryRef()
    geoms.append(geom.ExportToWkt())

pol = loads(geoms[0])

print(LineString(pol.exterior.coords).wkt)

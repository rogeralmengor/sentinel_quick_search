#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import geopandas as gpd  
import numpy as np  
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
import os
import sys
import time 
import gdal 
from gdal import *


def rasterize(src_vector: str,
              burn_attribute: str,
              src_raster_template: str,
              dst_rasterized: str,
              gdal_dtype: int = 3):
    """Rasterize the values of a spatial vector file.

    Arguments:
        src_vector {str}} -- A OGR vector file (e.g. GeoPackage, ESRI Shapefile) path containing the
            data to be rasterized.
        burn_attribute {str} -- The attribute of the vector data to be burned in the raster.
        src_raster_template {str} -- Path to a GDAL raster file to be used as template for the
            rasterized data.
        dst_rasterized {str} -- Path of the destination file.
        gdal_dtype {int} -- Numeric GDAL data type, defaults to 3 which is Int16.
            See https://github.com/mapbox/rasterio/blob/master/rasterio/dtypes.py for useful look-up
            tables.
    Returns:
        None
    """

    data = gdal.Open(str(src_raster_template),  # str for the case that a Path instance arrives here
                     gdalconst.GA_ReadOnly)
    geo_transform = data.GetGeoTransform()
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    mb_v = ogr.Open(src_vector)
    mb_l = mb_v.GetLayer()
    target_ds = gdal.GetDriverByName('GTiff').Create(dst_rasterized,
                                                     x_res, y_res, 1,
                                                     gdal_dtype)  # gdal.GDT_Byte
    # import osr
    target_ds.SetGeoTransform((geo_transform[0],  # x_min
                               geo_transform[1],  # pixel_width
                               0,
                               geo_transform[3],  # y_max
                               0,
                               geo_transform[5]  # pixel_height
                               ))
    prj = data.GetProjection()
    # srs = osr.SpatialReference(wkt=prj)  # Where was this needed?
    target_ds.SetProjection(prj)
    band = target_ds.GetRasterBand(1)
    # NoData_value = 0
    # band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(target_ds, [1], mb_l, options=[f"ATTRIBUTE={burn_attribute}"])

    target_ds = None


def main():
    
    start = time.time() 

    if len(sys.argv) < 5: 
        print("too few arguments")
        print("1. input_raster ")
        print("2. indir calvalus")
        print("3. outdir calvalus")
        print("4. geojson")
        sys.exit(0)
    
    input_raster = sys.argv[1]
    path_geojson = sys.argv[4] 
    outdir = sys.argv[3]
    class_code = "CLASS" 
    pid_code = "PIDS"
    proximity = "proximity"
    
    try: 
        os.makedirs("output")
    except Exception as e:
        print(e)
    
    osm = gpd.read_file(path_geojson)
    print(osm)
    
    print("Buffering geojson")
    def buff_point(point): 
        return point.buffer(5, cap_style=3)
    #buf = test.buffer(10, cap_style=3)
    osm["geometry"] = osm["geometry"].apply(buff_point)
    print(osm)
    buffered_path = os.path.basename(path_geojson).replace(".geojson", "_BUFFERED.geojson")
    osm.to_file("output" + "/" + buffered_path , driver = "GeoJSON")
    print(osm.crs)

    print("Rasterizing CLASS column")
    class_path = "output" + "/" + buffered_path.replace(".geojson", ".tif")
    rasterize(path_geojson, "CLASS", input_raster,class_path, gdal_dtype=2)
    
    print("Obtaining class array")
    class_ds = gdal.Open(class_path)
    class_arr_complete = np.array(class_ds.GetRasterBand(1).ReadAsArray())
    class_code_arr_valid_data = class_arr_complete[class_arr_complete != 0]
    print(class_code_arr_valid_data.shape)
    npy_class_path = "output" + "/" + "aux_vector_CLASS.npy" 
    np.save(npy_class_path, class_code_arr_valid_data) 
    print("-"*80)

    print("Obtaining  other arrays")
    columns = ["proximity", "GRLANDSCH", "PIDS"]
    for col in columns: 
        path = "output" + "/" + "aux_vector_" + col + ".npy"
        array = np.asarray(osm[col].to_list())
        print(array)
        np.save(path, array)

    print("Extraction values of input raster")
    src_ds = gdal.Open(input_raster)
    input_raster_array = np.array(src_ds.GetRasterBand(1).ReadAsArray())
    input_raster_valid_data = input_raster_array[class_arr_complete !=0]
    print(input_raster_valid_data.shape)
    print(input_raster_valid_data)
    npy_input_raster_path = "output" + "/" + os.path.basename(input_raster).replace(".tif", ".npy")
    np.save(npy_input_raster_path, input_raster_valid_data)


if __name__ == "__main__": 
    main()

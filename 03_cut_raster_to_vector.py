#!/usr/bin/env python3 
# -*- coding: ascii -*-

import gdal 
from gdal import * 
import subprocess 
import os 
import sys
from functools import wraps 
import time
import tempfile 
import numpy as np

__usage__ = """
--------------------------------------------------------------------------------
cut_raster_to_vector.py 
-----------------------

Description:
------------
    It follows the following steps: 
    1. Clips the output from step 1 with geojson file (see extra parameters) 
    2. Warp the output 2 to raster_s2 (see extra parameters) 

Parameters:
-----------
    input_s1            - str -> complete path to raster to be cut 
    input_s1_dir        - str -> automatically taken from input file
    output_dir          - str -> path where files will be stored (on calvalus)
    
Extra_params (in string blank space separated):
-----------------------------------------------
    raster_s2           - str -> complete path to s2 image that serves
                            to create a shapefile from which parameter 1
                            will be cut
    geojson_path        - str -> complete path to geojson in 4326 to cut the 
                            parameter 1 

Maintainer:
----------- 
    Roger Almengor Gonzalez

Dockerimage:
------------
    cvfeeder.eoc.dlr.de:5000/ra/snap_py:0.8
--------------------------------------------------------------------------------
"""

def get_extent_raster(raster_path):
    print("-"*80)
    print("Getting extent of {}".format(raster_path))
    ds = gdal.Open(raster_path, GA_ReadOnly)
    gt = ds.GetGeoTransform()
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + gt[1] * ds.RasterXSize
    miny = maxy + gt[5] * ds.RasterYSize
    return minx, maxy, maxx, miny


def clip_raster_to_geojson(geojson_path, raster_input):

    print("-"*80)
    print("cutting to line the output rasters")
    cl = os.path.basename(geojson_path).replace('.geojson', '')
    raster_output = os.path.basename(raster_input).replace('.tif', '_clip.tif')
    command = "gdalwarp" + " -t_srs EPSG:4326" + " -of GTiff" + " -cutline " + \
                geojson_path + " -cl " + cl + " -crop_to_cutline " + " " + \
                " -co COMPRESS=LZW " + " -co PREDICTOR=2 " + " -co ZLEVEL=9 " +\
                raster_input + " " + raster_output
            
    print(command)
    subprocess.call(command, shell=True)
    return raster_output


def change_gt_raster_with_other_raster(input_raster, extent_raster_path, output_raster):
    minx, maxy, maxx, miny = get_extent_raster(extent_raster_path)
    src_extent = gdal.Open(extent_raster_path)
    t_proj = osr.SpatialReference(wkt=src_extent.GetProjection())
    t_srs = t_proj.GetAttrValue('AUTHORITY', 1)
    src_input = gdal.Open(input_raster)
    s_proj = osr.SpatialReference(wkt=src_input.GetProjection())
    s_srs = s_proj.GetAttrValue('AUTHORITY', 1)
    command = f'gdalwarp -s_srs EPSG:{s_srs} -t_srs EPSG:{t_srs} -dstnodata -9999 -r near -of GTiff -co COMPRESS=LZW -tr 10 10 -te {minx} {miny} {maxx} {maxy} {input_raster} {output_raster}'
    print(command)
    subprocess.call(command, shell=True)
    return output_raster


def main():
   
    start_time = time.time()
    if len(sys.argv) < 5: 
        print(__usage__)
        exit(1)

    raster_to_cut = sys.argv[1]  
    calvalus_indir = sys.argv[2]  
    calvalus_outdir = sys.argv[3]  
    extra_parameters = sys.argv[4] 
    extra_parameters = extra_parameters.split(" ")
    geojson_path = extra_parameters[0]
    extent_raster_path = extra_parameters[1]

    try:
        os.makedirs("output")

    except Exception as e: 
        print(e) 

    minx, maxy, maxx, miny = get_extent_raster(extent_raster_path)
    second_output_path = clip_raster_to_geojson(geojson_path, raster_to_cut)
    final_output_path = "output" + "/" + os.path.basename(raster_to_cut)
    change_gt_raster_with_other_raster(second_output_path, extent_raster_path, final_output_path)
   
    processing_time = time.time() - start_time
    print("-- processing time {:.2f} seconds --".format(processing_time))

if __name__ == "__main__": 
    main()

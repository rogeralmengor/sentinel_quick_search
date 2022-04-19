#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__usage__ = """
-------------------------------------------------------------------------------
Name:
s1_mosaic.py
-------------------------------------------------------------------------------
Description:
    Reads a text file with complete paths to rasters to be mosaiced.
    The mosaic is done with no data value set to -999999.
    Data Type of output raster gdal.GDT_Int32
-------------------------------------------------------------------------------
Parameters: 
    1. text_file: complete path to text_file 
    2. filePath: complete path to folder containing parameter 1
    3. output_path: global output directory on calvalus
    4. filePath2: complete path to raster with extent to wrap final product
-------------------------------------------------------------------------------
Author:
Roger Almengor Gonzalez
-------------------------------------------------------------------------------
Dockerimage: 
    cvfeeder.eoc.dlr.de:5000/ra/snap_py:0.8
-------------------------------------------------------------------------------
"""

import os
import sys
import gdal  
from gdal import * 
import math
import time
import numpy as np
import shutil 

def get_extent(fn): 
    """Returns min_x, max_y, max_x, min_y"""
    print("opening {}".format(fn))
    ds = gdal.Open(fn)
    assert ds != None
    gt = ds.GetGeoTransform() 
    return (gt, gt[0], gt[3], gt[0] + gt[1] * ds.RasterXSize, 
            gt[3] + gt[5] * ds.RasterYSize)


def final_array_mosaic(array_1, array_2):
    final_array = np.zeros(array_1.shape)
    array_1 = np.where((array_1 == 0), -999999, array_1)
    print("ARRAY_1")
    print(array_1)
    array_2 = np.where((array_2 == 0), -999999, array_2)
    print("ARRAY_2")
    print(array_2)
    final_array = np.where(((array_1 == -999999) & (array_2 == -999999)), -999999, final_array)
    final_array = np.where(((array_1 == -999999) & (array_2 != -999999)), array_2, final_array)
    final_array = np.where(((array_1 != -999999) & (array_2 == -999999)), array_1, final_array)
    print(final_array)
    return final_array


def mosaic_calculations(path_1, path_2, path_extent, fp_basename): 
    print("opening .. {}".format(path_1))
    print("opening .. {}".format(path_2))
    
    ds_1 = gdal.Open(path_1)  
    ds_2 = gdal.Open(path_2)
    assert ds_1 != None
    assert ds_2 != None
    gt, min_x, max_y, max_x, min_y = get_extent(path_extent)
    driver = gdal.GetDriverByName('gtiff')
    print("creating output file")
    out_ds = driver.Create("output" + "/" + fp_basename.replace(".txt", ".tif"), 10980, 10980, 1, GDT_Int32, options = ["COMPRESS=LZW", "TILED=YES"])
    print("opening first array") 
    array1 = np.array(ds_1.GetRasterBand(1).ReadAsArray())
    print(array1)
    array2 = np.array(ds_2.GetRasterBand(1).ReadAsArray())
    print(array2)
    print("opening second array") 
    array_final = final_array_mosaic(array1, array2) 
    out_band = out_ds.GetRasterBand(1)
    print("Writing final array") 
    out_band.WriteArray(array_final)
    out_ds.SetGeoTransform(gt)
    in_ds_proj = gdal.Open(path_extent)
    proj = in_ds_proj.GetProjection()
    out_ds.SetProjection(gdal.Open(path_extent).GetProjection())
    out_ds.GetRasterBand(1).ComputeStatistics(True)
    out_ds.GetRasterBand(1).SetNoDataValue(-999999)
    out_ds.BuildOverviews('average', [2,4,6,8,16,32])
    del out_ds

def change_extent(path_to_file, path_extent, outputfile):
    ds = gdal.Open(path_to_file)
    gt, min_x, max_y, max_x, min_y = get_extent(path_extent)
    driver = gdal.GetDriverByName('gtiff')
    print("creating output file")
    out_ds = driver.Create(outputfile, 10980, 10980, 1, GDT_Int32, options = ["COMPRESS=LZW", "TILED=YES"])
    array = np.array(ds.GetRasterBand(1).ReadAsArray())
    array = np.where((array == 0), -999999, array)
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(-999999)
    out_band.WriteArray(array)
    out_ds.SetGeoTransform(gt)
    
    in_ds_proj = gdal.Open(path_extent)
    proj = in_ds_proj.GetProjection()
    out_ds.SetProjection(gdal.Open(path_extent).GetProjection())
    out_ds.GetRasterBand(1).ComputeStatistics(True)
    out_ds.GetRasterBand(1).SetNoDataValue(-999999)
    out_ds.BuildOverviews('average', [2,4,6,8,16,32])
    del out_ds


def main():
    
    start_time = time.time()
    if len(sys.argv) < 5:
        print(__usage__)
        exit(1) 
    
    file_extent = sys.argv[4] 
    in_files = open(sys.argv[1], 'r').read().splitlines()
    global_outdir = sys.argv[3]
    output_file = global_outdir + "/" + os.path.basename(sys.argv[1]).replace(".txt", ".tif")
    
    try: 
        os.makedirs("output")
    except Exception as e: 
        print(e)

    if os.path.exists(output_file): 
        print("File Already exists")
        exit(0)
    if len(in_files) < 2: 
        print("Not enough files to perform this operation")
        print("Copying first file")
        change_extent(in_files[0], file_extent, "output" + "/" + os.path.basename(sys.argv[1]).replace(".txt", ".tif"))
    
    else: 
        mosaic_calculations(in_files[0], in_files[1], file_extent, os.path.basename(sys.argv[1])) 
        print("Done!")
        print("---processing time {} seconds --".format(round(time.time() - start_time)))
    
if __name__ == "__main__":
    main()

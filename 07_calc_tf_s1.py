#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

import os 
import glob 
import datetime 
import pandas as pd 
import pprint as pprint 
import numpy as np 
import subprocess 
import gdal 
from gdal import * 
import time 
import rasterio 
from rasterio.merge import merge 
import re 
import sys 
from pprint import pprint
import tempfile 
import shutil
import tqdm
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")


__usage__="""

s1_calc_tf.py 
-------------------------------------------------------------------------------
Description: 
       calculates time features (min, max, mean, median) for sentinel-1 GRD 
-------------------------------------------------------------------------------
Parameters: 
        1. Path to one file containing the paths of data from which the stats
        will be calculated
        2. Base directory of parameter 1
        3. Global output folder in calvalus
-------------------------------------------------------------------------------
Maintainer: 
    Roger Almengor Gonzalez
-------------------------------------------------------------------------------
Project: 
    HICAM
-------------------------------------------------------------------------------
Date: 
    sept-09th-2020
-------------------------------------------------------------------------------
"""




def build_stats_overviews_set_nodata(out_ds):

    out_ds.FlushCache() 
    out_ds.GetRasterBand(1).ComputeStatistics(True)
    out_ds.GetRasterBand(1).SetNoDataValue(-999999)
    out_ds.BuildOverviews('average', [2,4,8,16,32])
    
    del out_ds
   

def calc_tf_s1(vrt_stack_path,  stats):

    in_ds = gdal.Open(vrt_stack_path)

    if in_ds == None: 
        print("CANNOT OPEN {}".format(vrt_stack_path))
        exit(0)

    crs = in_ds.GetProjection()
    gt = list(in_ds.GetGeoTransform())
    num_bands = in_ds.RasterCount
    in_band = in_ds.GetRasterBand(1)
    xsize = in_band.XSize
    ysize = in_band.YSize
    block_xsize, block_ysize = in_band.GetBlockSize() 
    nodata = in_band.GetNoDataValue()

    driver = gdal.GetDriverByName("GTiff")
    out_ds_mean = driver.Create(vrt_stack_path.replace(".vrt", "_mean.tif"), xsize, ysize, 1, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW"])
    out_ds_mean.SetProjection(in_ds.GetProjection())
    out_ds_mean.SetGeoTransform(in_ds.GetGeoTransform())
    out_band_mean = out_ds_mean.GetRasterBand(1)

    out_ds_min = driver.Create(vrt_stack_path.replace(".vrt", "_min.tif"), xsize, ysize, 1, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW"])
    out_ds_min.SetProjection(in_ds.GetProjection())
    out_ds_min.SetGeoTransform(in_ds.GetGeoTransform())
    out_band_min = out_ds_min.GetRasterBand(1)
    
    out_ds_max = driver.Create(vrt_stack_path.replace(".vrt", "_max.tif"), xsize, ysize, 1, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW"] )
    out_ds_max.SetProjection(in_ds.GetProjection())
    out_ds_max.SetGeoTransform(in_ds.GetGeoTransform())
    out_band_max = out_ds_max.GetRasterBand(1)


    out_ds_median = driver.Create(vrt_stack_path.replace(".vrt", "_median.tif"), xsize, ysize, 1, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW"] )
    out_ds_median.SetProjection(in_ds.GetProjection())
    out_ds_median.SetGeoTransform(in_ds.GetGeoTransform())
    out_band_median = out_ds_median.GetRasterBand(1)

    
    for x in tqdm(range(0, xsize, block_xsize)):
        if x + block_xsize < xsize: 
            cols = block_xsize
        else:
            cols = xsize - x 
        
        for y in range(0, ysize, block_ysize): 
            if y + block_ysize < ysize: 
                rows = block_ysize
            else: 
                rows = ysize - y
                
            # final array creation 
            num_pixels = rows*cols
            final_array = np.zeros((num_bands, num_pixels), dtype=np.float32)
            final_array = final_array.reshape(num_bands, num_pixels)

            for i in range(num_bands): 
                
                # Fetching input raster 
                in_band = in_ds.GetRasterBand(i+1)
                data = in_band.ReadAsArray(x, y, cols, rows)
                
                #Flattening array
                data = data.flatten()
                
                # Performing masking
                data = np.where(data == -999999, np.nan, data)
                data = np.where(data <= - 30, np.nan, data)
                data = data.astype(np.float32)
               
               # Plugging values from calculation to final array[row-wise]
                final_array[i, :] = data

           # Calculation of stat, and reshaping array to block size 
            for stat in stats: 
                if stat == "mean":
                    array_mean = np.nanmean(final_array, axis=0)
                    array_mean[np.isnan(array_mean)] = -999999
                    array_mean = array_mean.reshape(rows, cols)
                    out_band_mean.WriteArray(array_mean, x, y) 
                
                elif stat == "median":
                    array_median = np.nanmedian(final_array, axis=0)
                    array_median[np.isnan(array_median)] = -999999
                    array_median = array_median.reshape(rows, cols)
                    out_band_median.WriteArray(array_median, x, y) 

                elif stat == "std":
                    array_std = np.nanstd(final_array, axis=0)
                    array_std[np.isnan(array_std)] = -999999
                    array_std = array_std.reshape(rows, cols)
                    out_band_std.WriteArray(array_std, x, y) 

                elif stat == "min":
                    array_min = np.nanmin(final_array, axis=0)
                    array_min[np.isnan(array_min)] = -999999
                    array_min = array_min.reshape(rows, cols)
                    out_band_min.WriteArray(array_min, x, y) 
                
                elif stat == "max":
                    array_max = np.nanmax(final_array, axis=0)
                    array_max[np.isnan(array_max)] = -999999
                    array_max = array_max.reshape(rows, cols)
                    out_band_max.WriteArray(array_max, x, y) 
                
                elif stat == "count":
                    out_ds_count = driver.Create(vrt_stack_path.replace(".vrt", "_count.tif"),xsize, ysize, 1, in_band.DataType)
                    out_ds_count.SetProjection(in_ds.GetProjection())
                    out_ds_count.SetGeoTransform(in_ds.GetGeoTransform())
                    out_band_count = out_ds_count.GetRasterBand(1)
                    array = np.nancount(final_array, axis=0)
                    array_count[np.isnan(array_count)] = -999999
                    array_count = array_count.reshape(rows, cols)
                    out_band_count.WriteArray(array_count, x, y) 

                else: 
                   print("{} not supported.".format(stat))
                   exit(1)
    
    build_stats_overviews_set_nodata(out_ds_max)
    build_stats_overviews_set_nodata(out_ds_mean)
    build_stats_overviews_set_nodata(out_ds_min)
     

def main(): 
    
    start_time = time.time()    

    fp = sys.argv[1]
    indir_global = sys.argv[2]
    outdir_global = sys.argv[3]

    try:
        outdir = "output"
        os.makedirs("output")
    
    except Exception:
        pass

    raster_paths = []
    with open(fp, "r") as fd: 
        for line in fd:
            line = line.replace("\r", "").replace("\n", "")
            raster_paths.append(line)
    
    outvrt_band_path = "output" + "/" + os.path.basename(fp).replace(".txt", "") + ".vrt"
    gdal.BuildVRT(outvrt_band_path, raster_paths, separate=True) 
    calc_tf_s1(outvrt_band_path,  ["mean", "min", "max", "median"])

    end_time = time.time()
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("processing time.") 
    print("{}hours : {}minutes: {}seconds".format(int(hours), int(minutes), seconds))
    print("Done!")
    print("-"*80)


if __name__ == "__main__": 
    main()

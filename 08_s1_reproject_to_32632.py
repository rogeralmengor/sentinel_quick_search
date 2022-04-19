#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__usage__ = """
-------------------------------------------------------------------------------
Name:
s1_reproject_to_32632.py
-------------------------------------------------------------------------------
Description:
For GeoTiffs found in the 33 UTM N will reproject them to 32UTM 
-------------------------------------------------------------------------------
Parameters: 
1. Complete path to geotiff 
2. filePath: complete path to folder containing parameter 1
3. output_path: global output directory on calvalus
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
import time
import tempfile 
import subprocess
import numpy as np
import rasterio 
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reproject_raster_in_wgs84_II(raster_input_path, raster_output_path): 
    dst_crs = 'EPSG:4326'
    with rasterio.open(raster_input_path) as src: 
        transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs, 
            'transform': transform, 
            'width': width, 
            'height': height, 
            'compress': 'lzw', 
            })

        with rasterio.open(raster_output_path, 'w', **kwargs) as dst: 
            for i in range(1, src.count + 1): 
                reproject(
                        source = rasterio.band(src, i), 
                        destination=rasterio.band(dst, i), 
                        src_transform=src.transform, 
                        src_crs=src.crs, 
                        dst_transform=transform, 
                        dst_crs=dst_crs, 
                        resampling=Resampling.nearest)


def reproject_raster_in_wgs84(raster_input_path, raster_output_path): 
    
    kwargs = {'format': 'GTiff', 'dstSRS': 'EPSG:4326', 'width':10980, 'height':10980}
    gdal.Warp(raster_input_path, raster_output_path, **kwargs)


def reproject_raster(raster_input_path, raster_output_path): 
    
    kwargs = {'format': 'GTiff', 'dstSRS': 'EPSG:32632', 'xRes':10, 'yRes':10}
    gdal.Warp(raster_input_path, raster_output_path, **kwargs)


def return_ds_from_path(input_raster_path): 
    
    ds = gdal.Open(input_raster_path)
    return ds 


def fetch_raster_band(ds, band_num): 
    
    band = ds.GetRasterBand(band_num)
    return band


def fetch_dtype(band): 

    dtype = gdal.GetDataTypeName(band.DataType)
    return dtype 


def create_output_raster(input_raster_path, output_raster_path): 
    creation_options = ["COMPRESS=LZW", "TILED=YES"]
    driver = gdal.GetDriverByName("GTiff")
    ds = return_ds_from_path(input_raster_path)
    rows = ds.RasterXSize
    cols = ds.RasterYSize
    out_ds = driver.Create(
                output_raster_path, 
                rows, 
                cols,
                1,
                GDT_Float32, 
                options = creation_options)
    return out_ds 


def return_array_from_ds(ds): 

    array = np.array(ds.GetRasterBand(1).ReadAsArray())
    return array


def fetch_geotransform_from_ds(ds): 

    gt = list(ds.GetGeoTransform())
    return gt 


def set_geotransform_in_ds(ds, gt): 

    ds.SetGeoTransform(gt)


def fetch_projection_from_ds(ds): 

    proj = ds.GetProjection() 
    return proj 


def set_projection_in_ds(ds, proj): 

    ds.SetProjection(proj)


def substitute_array_values(array, old_value, new_value): 
    array[array==old_value] = new_value
    return array 


def write_data_in_band(data, band): 

    band.WriteArray(data)


def change_no_data(input_raster_path, 
                    output_raster_path, 
                    old_value, 
                    new_value): 

    ds = return_ds_from_path(input_raster_path)

    out_ds = create_output_raster(input_raster_path, output_raster_path) 

    array = return_array_from_ds(ds)

    array = substitute_array_values(array, old_value, new_value)

    out_band = fetch_raster_band(out_ds, 1)

    write_data_in_band(array, out_band)

    gt = fetch_geotransform_from_ds(ds)

    set_geotransform_in_ds(out_ds, gt)

    proj = fetch_projection_from_ds(ds) 

    set_projection_in_ds(out_ds, proj) 

    out_ds.GetRasterBand(1).ComputeStatistics(True) 

    out_ds.GetRasterBand(1).SetNoDataValue(new_value)
    
    out_ds.BuildOverviews('average', [2,4,6,8,16,32])

    del out_ds



def main():
    
    start_time = time.time()
    if len(sys.argv) < 4:
        print(__usage__)
        exit(1) 
    
    raster_path = sys.argv[1]
    
    try: 
        os.makedirs("output")
    except Exception as e: 
        print(e)
    
    # create temp dir for prelim results  
    temp_dir_path = tempfile.mkdtemp()

    print("-- first reprojection to WGS84 --")
    reprojected_raster_path_wgs84 = temp_dir_path + "/" +\
            os.path.basename(raster_path).replace(".tif", "_wgs84.tif")
    #reproject_raster_in_wgs84(reprojected_raster_path_wgs84, raster_path)
    reproject_raster_in_wgs84_II(raster_path, reprojected_raster_path_wgs84)

    print("-- second reprojection to EPGS:32632 --")
    reprojected_raster_path = temp_dir_path + "/" + os.path.basename(raster_path)
    reproject_raster(reprojected_raster_path, reprojected_raster_path_wgs84)

    print("-- setting the no data and storing the final result in output --")
    final_raster = "output" + "/" + os.path.basename(raster_path)
    change_no_data(reprojected_raster_path, final_raster, 0, -999999) 
   
    print("---  processing time {} seconds ---".format(round(time.time() - start_time)))


if __name__ == "__main__":
    main()

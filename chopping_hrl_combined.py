#!/usr/bin/env python3
"""
chopping_hrl_combined.py

    I made this script to chop the HRL from copernicus land monitoring services to different
    tile grids. The grids are hard coded, but you can modify the script so it will accept 
    the grids from the the s2_tile_grid for Germany that you defined. (TODO:) 

    For more information run 
        python chopping_hrl_combined.py -h 
"""
import re 
import time 
import sys 
import tempfile
import os 
import geopandas as gpd
import tqdm 
from tqdm import tqdm 
import argparse
import subprocess
import gdal 
import osr 
import tempfile

import os

proj_folder = r"C:\Users\alme_ro\Miniconda3\envs\geoprocessing\Library\share\proj"
gdal_data_folder = r"C:\Users\alme_ro\Miniconda3\envs\geoprocessing\Library\share"

os.environ['PROJ_LIB'] = proj_folder 
os.environ['GDAL_DATA'] = gdal_data_folder 
gdal_warp = r"C:\Users\alme_ro\Miniconda3\envs\geoprocessing\Library\bin\gdalwarp.exe"

def parseArguments(): 
    # Create argument parser
    parser = argparse.ArgumentParser(description= __doc__)

    # Positional mandatory arguments

    parser.add_argument("-p", help="Complete path to s2 tile grid in geojson format.",\
            type=str, required=True, metavar="")

    parser.add_argument("-o", help="Complete path to output directory where results will be stored.",\
                        type=str, required = True, metavar="")

    parser.add_argument("-m", help="Complete path to folder where the muster rasters are located.",\
                        type=str, required=True, metavar="") 
    
    parser.add_argument("-r", help="Complete path to HRL raster to be chopped into pieces mwahahahaha!.",\
                        type=str, required=True, metavar="") 
    
    # Parse arguments
    args = parser.parse_args()

    return args

def extract_s2_tile_from_s2_grid(gdf, tile): 

    gdf = gdf.loc[gdf["Name"] == tile]
    
    return gdf 

def gdal_command_clip(raster, shapefile, tile, output_raster_path, s_srs, t_srs):

    commands = ['gdalwarp', 
                f'-s_srs EPSG:{str(s_srs)}',
                f'-t_srs EPSG:{str(t_srs)}',
                '-of GTiff',
                f'-cutline {shapefile}', 
                f'-cl {tile}',
                f'-crop_to_cutline {raster}',
                f'{output_raster_path}']

    command = ' '.join(commands) 
    print(command)
    subprocess.call(command, shell=True)

    return output_raster_path



def gdal_command_reprojecting(s_srs,
                            t_srs,
                            extent,
                            resX,
                            resY,
                            input_raster_path,
                            output_raster_path):

    #f'-te 699960.0 5490240.0 809760.0 5600040.0'
    commands =['gdalwarp', 
    f'-s_srs EPSG:{str(s_srs)}', 
    f'-t_srs EPSG:{str(t_srs)}',
    '-r near', 
    f'-te {extent[0][0]} {extent[1][1]} {extent[2][0]} {extent[3][1]}',
    '-ot Byte', 
    '-of GTiff',
    '-co COMPRESS=DEFLATE',
    '-co PREDICTOR=2',
    '-co ZLEVEL=9',
    f'-tr {str(resX)} {str(resY)}', 
    f'{input_raster_path}',
    f'{output_raster_path}'
    ]
    command = ' '.join(commands)
    print(command) 
    subprocess.call(command, shell=True)

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform
        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner (list)
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            print (x,y)
        yarr.reverse()
    return ext

def get_epsg_code(path): 
    ds = gdal.Open(path)
    proj = osr.SpatialReference(wkt=ds.GetProjection())
    epsg =  proj.GetAttrValue('AUTHORITY',1)
    print(epsg)
    return epsg  

def main(): 

    args = parseArguments()
    
    s2_tile_grid_path = args.p 
    output_folder = args.o 
    input_directory_with_musters = args.m
    input_hrl = args.r
    tiles = ["32ULC"]
#    tiles = ["31UGR", "31UGS", "31UGT", 
#            "32ULA", "32ULB", "32ULD", "32ULE", "32ULU", "32ULV",
#            "32UMA", "32UMB", "32UMC", "32UMD", "32UME", "32UMF", "32UMG", "32UMU", "32UMV", 
#            "32UNA", "32UNB", "32UNC", "32UND", "32UNE", "32UNF", "32UNU", "32UNV",
#            "32UPA", "32UPB", "32UPC", "32UPD", "32UPE", "32UPF" , "32UPU", "32UPV",
#            "32UQA", "32UQB", "32UQC", "32UQD", "32UQE", "32UQU", "32UQV", 
#            "33TUN", "32TLT", "32TNT", "32TMT", "32TPT", "32TQT", "33TUN",
#            "33UUA", "33UUP", "33UUQ", "33UUR", "33UUS", "33UUT", "33UUU", "33UUV",
#             "33UVA", "33UVP", "33UVQ", "33UVS", "33UVT", "33UVU", "33UVV"  
#            ]
    print(len(tiles))

    for tile in tqdm(tiles): 
        gdf = gpd.read_file(s2_tile_grid_path)
        gdf = extract_s2_tile_from_s2_grid(gdf, tile)
        temp_folder = tempfile.mkdtemp()
        gdf = gpd.GeoDataFrame(gdf)
        temp_shapefile_path = output_folder + "/" + tile + ".shp"
        print("Exporting s2 tile as shapefile..")
        gdf.to_file(temp_shapefile_path)

        print("Getting the raster set that will serve as 'muster'")
        raster_muster = [os.path.join(root, filename) for root, subdirs, filenames\
               in os.walk(input_directory_with_musters) for filename in filenames 
               if filename.startswith(tile)][0]
        in_ds = gdal.Open(raster_muster)
        in_band = in_ds.GetRasterBand(1)
        xsize = in_band.XSize
        ysize = in_band.YSize
        geotransform = in_ds.GetGeoTransform()
        print("Getting the extent of the raster muster..")
        ext = GetExtent(geotransform, xsize, ysize)
        temp_raster_file = output_folder + "/" + tile +  "_temp.tif"
        s_srs = get_epsg_code(input_hrl)
        print("Performing clipping of raster dateset with s2 tile..")
        hrl_clipped = gdal_command_clip(input_hrl, temp_shapefile_path, tile, temp_raster_file, s_srs, 4326) 
        print(hrl_clipped)
        print(type(hrl_clipped)) 
        s_srs = get_epsg_code(hrl_clipped)
        t_srs = get_epsg_code(raster_muster)
        output_file = output_folder + "/" + tile + ".tif"
        print("Performing reprojection..")
        gdal_command_reprojecting(s_srs, t_srs, ext, 10, 10, hrl_clipped, output_file) 

if __name__ == "__main__":
    main()

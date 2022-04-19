#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import geopandas as gpd 
import pprint 
from pprint import pprint 
import os 
import sys 

__help__ = """
-------------------------------------------------------------------------------
download_s1_footprints_as_geojson.py

------------------------------------
Description: 
-----------
Extract the S2-Tile from the S2_GRD file found at: 
/calvalus/home/alme_ro/Ancillary_Data/sentinel_2_index_shapefile.geojson 
Once that S2 tile is stored as geojson, is used as aoi to make a query of 
sentinel-1 data with fix parameters found in the function: 
    download_footprints_tile. 
You can modify this parameters according to your needs. 
The S2-index Tile and the scene query will be stored in the output directory

Parameters: 
-----------
1. /calvalus/home/alme_ro/Ancillary_Data/sentinel_2_index_shapefile.geojson
2. base directory taken from parameter 1. 
3. output directory on calvalus where output data will be stored. 

Extra Parameters string with comma separated: 
----------------
S2-Tile: e.g. 32TLT 
Orbit Direction: e.g. orbitdirection=Descending or orbitdirection=Ascending
user_name: user name from copernicus hub
password: password from your account in copernicus hub
start_date: e.g  "20180101"
end_date: e.g. "20180131" 

Maintainer: 
----------
Roger Almengor Gonzalez 

Docker image: 
------------
cvfeeder.eoc.dlr.de:5000/ra/snap_py:1.1
-------------------------------------------------------------------------------
"""

def extract_s2_tile_from_s2_grid(gdf, tile): 

    gdf = gdf.loc[gdf["Name"] == tile]
    return gdf 


def download_footprints_tile(aoi_geojson, path, orbit_direction, user, password, start, end): 

    """
    Downloads footprints using sentinelsat API. Modify start, end, 
    product_type and/or sentinel parameters according to your needs.
    """

    product_type = "GRD"
    sentinel = "1"
    subprocess.call(f"sentinelsat --geometry {aoi_geojson} \
                        -s {start} -e {end} \
                        -u {user} -p {password} \
                        --sentinel {sentinel} \
                        --path {path} \
                        --producttype {product_type} \
                        --footprints \
                        -q {orbit_direction}", shell=True)

def main(): 

    if len(sys.argv) < 4: 
        print(__help__)
        exit(1)

    try: 
        os.makedirs("output")

    except Exception as e: 
        print(e)


    s2_index_world_path = sys.argv[1]
    in_dir_calvalus = sys.argv[2]
    out_dir_calvalus = sys.argv[3]

    extra_parameters = sys.argv[4]
    extra_parameters = extra_parameters.split(" ")
    tile = extra_parameters[0]
    orbit_direction = extra_parameters[1]
    user_name = extra_parameters[2]
    password = extra_parameters[3]
    start_date = extra_parameters[4]
    end_date = extra_parameters[5]

    s2_index_world_gdf = gpd.read_file(s2_index_world_path)
    s2_index_tile = extract_s2_tile_from_s2_grid(s2_index_world_gdf, tile)
    s2_index_path = "output" + "/" + tile + ".geojson"
    s2_index_tile.to_file(s2_index_path, driver = "GeoJSON")
    download_footprints_tile(s2_index_path ,"output", orbit_direction, user_name, password, start_date, end_date)
    
    if orbit_direction == "orbitdirection=Descending": 
        suffix = "desc"
    elif orbit_direction == "orbitdirection=Ascending": 
        suffix = "asc"
    
    new_name = "search_footprints.geojson".replace("search", tile + "_search")
    new_name = new_name.replace(".geojson", "_" + suffix + "_" + start_date + "TO" + end_date + ".geojson") 
    os.rename("output" + "/" + "search_footprints.geojson", "output" + "/" + new_name )

    
if __name__ == "__main__": 
    main() 

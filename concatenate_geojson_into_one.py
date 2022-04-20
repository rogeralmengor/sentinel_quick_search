#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import geopandas as gpd 
import os 
import sys 
from tqdm import tqdm 
from pprint import pprint 
import time
import pandas as pd

def main():

    __help__ = """
    concatenate_geojson_into_one.py

    List of parameters 
    ==================
     1. input geojson file  
     2. output path to file that will be written

     Note: 
     ---
     All files must be located into the same directory than 
     file number 1.
    """

    start = time.time()

    if len(sys.argv) < 3: 
        print(__help__)
        sys.exit(1) 

    path_to_geojson = sys.argv[1]
    outfile = sys.argv[2]

    print("creating list of geojson files")
    geojson_files = [ os.path.join(os.path.dirname(path_to_geojson), filename) \
        for filename in next(os.walk(os.path.dirname(path_to_geojson)))[2] if \
            filename.endswith("final.geojson")]
    
    pprint(geojson_files)
    list_of_geodataframes = []
    for f in tqdm(geojson_files): 
        f = gpd.read_file(f)
        list_of_geodataframes.append(f);

    print("combining them into a single geodataframe..")
    combined_geojson = gpd.GeoDataFrame(pd.concat(list_of_geodataframes,\
                        ignore_index = True)) 

    print(combined_geojson)

    print("creating output folder..")
    try: 
        os.mkdir(os.path.dirname(outfile))
    except Exception as e: 
        print(e)
    
    print("exporting dataset as geopackage..")
    combined_geojson.to_file(outfile)

    processing_time = time.time() - start
    processing_time = str(round(processing_time, 2))

    print(f"Processing time {processing_time}")


if __name__ == "__main__": 
    main() 
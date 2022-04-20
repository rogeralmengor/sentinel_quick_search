#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Downloads footprints of sentinel-1 imagery
 as geojson file format using the api and a
AOI (Area of Interest)
"""

import argparse 
import subprocess
import geopandas as gpd 
import os 
import sys 


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

def parseArguments(): 
    
    # Create argument parser
    parser = argparse.ArgumentParser(description= __doc__)

    # Positional mandatory arguments
    parser.add_argument('-ip', help='Input Path aoi in geojson Format', \
        type=str, required=True, metavar='')
    
    parser.add_argument('-of', help='Output folder where to store results', \
        type=str, required=True, metavar='')

    parser.add_argument('-od', help='Orbit Direction',\
         type=str, required = True, choices=['Descending', 'Ascending'], metavar='')

    parser.add_argument('-u', help = 'User', type = str, required = True, metavar='')

    parser.add_argument('-p', help = 'Password', type = str, required = True, metavar = '')

    parser.add_argument('-s', help = 'start date: e.g.: "20180101"', type = str, required = True, metavar = '')

    parser.add_argument('-e', help = 'end date: e.g.: "20180131', type = str, required = True, metavar = '')
    
    # Parse arguments
    
    args = parser.parse_args()
    
    return args



def main(): 

    args = parseArguments()
    orbit_direction = args.od 
    orbit_direction="orbitdirection="+orbit_direction
    user_name = args.u 
    password = args.p 
    start_date = args.s 
    end_date = args.e
    output_folder = args.of 
    input_path = args.ip

    try: 
        os.makedirs(output_folder)

    except Exception as e: 
        print(e)
    import pdb; pdb.set_trace()
    download_footprints_tile(input_path ,
                            output_folder,
                            orbit_direction,
                            user_name,
                            password,
                            start_date,
                            end_date)
    
if __name__ == "__main__": 
    main() 
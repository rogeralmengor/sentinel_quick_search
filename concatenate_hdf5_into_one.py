#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 
import os 
import sys 
from tqdm import tqdm 
from pprint import pprint 

def main():

    __help__ = """
    concatenate_csvs_into_one.py

    List of parameters 
    ==================
     1. input hdf file 
     2. input base dir taken from arg 1 
     3. output dir where results will be stored in calvalus
    """
    if len(sys.argv) < 4: 
        print(__help__)
        sys.exit(1) 

    sampsize = 7000 
    pid = "PID"
    max_num_of_pixels_per_polygon = 1
    path_to_hdf = sys.argv[1]
    path = sys.argv[2] 
    outdir_calvalus = sys.argv[3]

    print("\nCREATES LIST OF HDF5 FILES IN PATH")
    print("=================================")
    hdf_files = [ os.path.join(path, filename) for filename in next(os.walk(path))[2] if filename.endswith("_selected.h5")]
    pprint(hdf_files)

    print("\nCHECKS IF COLUMNS ARE THE SAME ACROSS DATAFRAMES")
    print("AND EXITS WITH ERROR (1) IF CONDITION IS NOT TRUE")
    print("=================================================")
    for hdf_file in tqdm(hdf_files):
        num_cols = len(pd.read_hdf(hdf_file, key = "df").columns)
        if num_cols < 1080:
            print(f"{hdf_file} does not match to the minimum cols required")
            sys.exit(1)

    print("\nCOMBINES THEM INTO A SINGLE DATAFRAME")
    print("====================================")
    combined_hdf = pd.concat([pd.read_hdf(f, "df") for f in tqdm(hdf_files)], join="inner")
    print("columns in combined data frame")
    print(len(combined_hdf.columns))
    print(combined_hdf.columns)

    print("\nMAKES A SECOND CLEANING OF THE LARGEST DATASET SELECTING ONLY ONE") 
    print("OBSERVATION PER POLYGON ID AND EXPORTING AS HDF5") 
    print("==================================================================")
    combined_hdf = combined_hdf.sample(frac=1).drop_duplicates(['aux_vector_PID'])
   
    print("\nCREATING LOCAL OUTPUT FOLDER")
    print("==============================")
    try: 
        os.mkdir("output")
    except Exception as e: 
        print(e)
    
    print("\nEXPORTING COMBINED DATASET AS HDF")
    print("===================================")
    combined_hdf_file_path = "output" + "/" + "COMBINED.h5"
    combined_hdf.to_hdf(combined_hdf_file_path, key = "df")
    check_df = pd.read_hdf(combined_hdf_file_path, "df")
    print(check_df)


if __name__ == "__main__": 
    main() 

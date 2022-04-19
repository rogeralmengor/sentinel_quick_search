#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 
import os 
import sys 


def main():

    __help__ = """
    export_csv_as_hdf.py
    ---------------------
    Small script to take a csv file, select
    one observation per aux_vector_PID (column with a 
    polygon identifier, obtaing when using gdal_subset_samples.py)
    and export it as h5 (hdf5) file format

    List of parameters 
    ==================
     1. input csv file 
     2. input base dir taken from arg 1 
     3. output dir where results will be stored in calvalus

     Assumption: 
     ==========
     The CSV File must have a column called aux_vector_PID, 
     and a number of columns at least of 1080, if not, 
     there is a sys exit call. The values next to the polygon's
     border will be deleted aux_vector_proximity > 1 will be 
     kept. 
    """
    if len(sys.argv) < 4: 
        print(__help__)
        sys.exit(1) 

    pid = "PID"
    path_to_csv = sys.argv[1]
    path = sys.argv[2] 
    outdir_calvalus = sys.argv[3]

    try: 
        os.mkdir("output")

    except Exception as e: 
        print(e)

    # Checking number of columns 
    # ==========================
    num_cols = len(pd.read_csv(path_to_csv).columns)
    if num_cols < 1080:
        print(csv_file)
        print(num_cols)
        print("Number of columns less than 1080")
        sys.exit(1)

    # Checking if output already exists  
    # =================================
    output_hdfs_path =  sys.argv[3] + "/" + os.path.basename(path_to_csv).replace("csv", "h5")
    if os.path.exists(output_hdfs_path): 
        print(f"h5 for {csv_file} already exists")
        sys.exit(1)
    
    # Reading csv file as pandas dataframe 
    # ===================================
    df = pd.read_csv(path_to_csv)
    
    # Droping duplicates
    # ===================
    df = df.sample(frac=1).drop_duplicates(['aux_vector_PID'])
    df = df[df['aux_proximity'] > 1.0]

    try:
        # Droping columns that contains Un as suffix
        df = df[df.columns.drop(list(df.filter(regex='Un')))]

    except Exception as e: 
        print(e) 

    print(df)
    print(df.aux_vector_PID)
    print(len(df))

    # Exporting hdf in temporal output folder  
    # =======================================
    temp_hdfs_path = "output" + "/" + os.path.basename(path_to_csv).replace("csv", "h5")
    df.to_hdf(temp_hdfs_path, key="df")


if __name__ == "__main__": 
    main() 

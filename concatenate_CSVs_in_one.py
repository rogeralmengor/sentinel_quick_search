#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 
import os 
import time 
import sys 
from pprint import pprint 
from tqdm import tqdm 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from eobox.ml import plot_confusion_matrix, predict_extended
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import tempfile


__help__ = """
-------------------------------------------------------------------------------
concatenate_CSVs_in_one.py 

Description:
-----------
Concatenates csvs files with the same structure (columns and index) into a 
single CSVs and exports it. The csv contains a subset of the concatenated
csv, where a maximum number of pixels, and a sample size
(sampsize variable), provided by the user

Parameters:
----------
1. CSV file                 - complete path to one of the csv files that will
                              be concatenated
2. Input Folder on Calvalus - Based dir, automatically taken from parameter 1
3. outdir                   - directory where results will be stored

Extra Parameters: 
----------------
1. name_of_table       - name of the table that will store the stats
2. number_of_samples   - number of samples per class
3. class_col           - column with class id
4. col_pid             - column PID (code containing the Polygon ID)

Docker Image: 
cvfeeder.eoc.dlr.de:5000/ra/classification:0.3
-------------------------------------------------------------------------------
"""


def get_unique_classes_in_df(df, col): 

    class_codes = df["aux_vector_" + col].unique().tolist() 
    return class_codes 


def random_selection_within_subsets(df, col, sampsize): 
    
    """
    Selects a given number of elements per col

    Parameters: 
    -----------
    1. df        - Pandas Dataframe
    2. col       - column from which the selection of max elemnts will be made
    3. sampsize  - Number of elements to extract from dataframe per col value
    """

    class_codes = get_unique_classes_in_df(df, col)
    column_list = df.columns.tolist() 
    out_df = pd.DataFrame(columns=column_list)
    
    for class_code in tqdm(class_codes): 
        
        tmp_df = df[df["aux_vector_" + col] == class_code]
        
        if len(tmp_df) < int(sampsize):
            print(f"Sampling all elements for {class_code}")
            print(f"Number of pixels {len(tmp_df)}")
            subset_per_class = tmp_df.sample(n=len(tmp_df), replace = False)
            out_df = pd.concat([out_df, subset_per_class], ignore_index=True)
        
        else:
            print(f"Sampling {sampsize} for class {class_code}")
            subset_per_class = tmp_df.sample(n=int(sampsize), replace=False)
            print(f"Number of pixels {len(subset_per_class)}")
            out_df = pd.concat([out_df, subset_per_class], ignore_index=True)
    
    return out_df


def main(): 
    
    start = time.time() 

    if len(sys.argv) < 4:
        print(__help__)
        exit(1)
    
    print("Reading input parameters") 

    csv_file = sys.argv[1]
    indir_calvalus = sys.argv[2]
    outdir_calvalus = sys.argv[3]
    options = sys.argv[4]
    extra_params = options.split(" ")
    max_num_of_pixels_per_polygon = 1 
    name_of_table = extra_params[0]
    sampsize = extra_params[1]
    col_class = extra_params[2]
    col_pid = extra_params[3]

    upperdir = os.path.dirname(indir_calvalus)
    upperdir = os.path.dirname(upperdir)

    print("Iterating over in the upperdir variable (directory), and find csv files")
    print("ignoring the ones called 'product-sets.csv'") 
    csv_files = [os.path.join(root, csv_path) for root, subdirs, files in \
                os.walk(upperdir) for csv_path in files if \
                (csv_path.endswith("csv") and not \
                csv_path.endswith("product-sets.csv"))]
    assert len(csv_files) > 0, "list of csv files is empty"

    try: 
        os.makedirs("output")

    except Exception as e: 
        print(e)
    
    print("create temporal folder to store filtered version of csv files stored")
    print("in the following bucle") 
    temporal_folder = tempfile.mkdtemp() 

    for csv_file in tqdm(csv_files): 
        
        print("reading csv file")
        df = pd.read_csv(csv_file)
        
        print("deleting proximity values from dataframe <= 1.0") 
        df = df[df.aux_proximity > 1.0]
        
        print("selecting one pixel from every polygon")
        df = random_selection_within_subsets(
                    df,
                    col_pid,
                    max_num_of_pixels_per_polygon)

        print("selecting only 1000 samples per class")
        print("1000 is used to assure that clusters of some crops")
        print("found in a sentinel-2 tile are sampled with a") 
        print("sample size which is big enough for statistical")
        print("analysis") 
        df = random_selection_within_subsets(df, col_class, 1000) 
        
        print("exporting dataframe in temp folder as csv file") 
        df.to_csv(temporal_folder + "/" + os.path.basename(csv_file))
        print("-"*80)
    
    print("creating list of csv files in temp folder") 
    csv_files = [os.path.join(root, f) for root, subdirs, filenames in\
                os.walk(temporal_folder) for f in filenames\
                if f.endswith(".csv")]
    assert len(csv_files) > 0, "list of csv files is empty"

    print("combining CSV and applying join=inner to avoid columns that are repeated") 
    print("in all CSV")
    combined_csv = pd.concat([pd.read_csv(f) for f in csv_files], join="inner")
    
    #print("deleting all values that are on borders proximity != 1.0") 
    #combined_csv = combined_csv[combined_csv.aux_proximity > 1.0]
    #print(combined_csv)
    
    print(f"Extracting only {max_num_of_pixels_per_polygon} pixels per polygon to") 
    print("avoid duplication of polygons found in two different Sentinel-2 Tile") 
    combined_csv = random_selection_within_subsets(
                    combined_csv,
                    col_pid,
                    max_num_of_pixels_per_polygon) 

    # Grouping by aux_vector_pid and calculating median
    # In this step the geometry information is lost
    #combined_csv = combined_csv.groupby(
                    #["aux_vector_pid"],
                    # as_index=False,
                    # sort=False).median()
    
    combined_csv = combined_csv.reset_index()
    
    print(f"Taking only number of samples per class: {sampsize}") 
    combined_csv = random_selection_within_subsets(
                    combined_csv,
                    col_class,
                    sampsize)

    column_names = [x for x in combined_csv.columns]
   
    print("creating a list of columns that are not part of the raster layers list")
    print("rasters used as input starts with 'S'")
    columns_to_drop = [x for x in column_names if not x.startswith("S")]

    X = combined_csv.drop(columns_to_drop, axis = 1, inplace=False)
    y = combined_csv["aux_vector_" + col_class]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    print("Training the classification model")
    rf_clf = RandomForestClassifier(n_estimators=300,
                                    oob_score=True,
                                    n_jobs=-1,
                                    random_state=123)

    rf_clf = rf_clf.fit(X_train, y_train)

    print("Validation of the classification model") 
    y_pred = rf_clf.predict(X_test)
    
    class_report_txt_file = "output" + "/" + "classification_report.txt"
    print(classification_report(y_test, y_pred)) 
    with open(class_report_txt_file, "w") as f:
        print(classification_report(y_test, y_pred), file=f)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    class_codes = np.unique(y_train)

    print("Saving confusion matrix as PNG file") 
    cm = confusion_matrix(y_test, y_pred)
    ax = plot_confusion_matrix(cm,
                               class_names=sorted(class_codes),
                               switch_axes=True,
                               ax=ax,
                               cmap=plt.cm.Greys)

    fig.savefig("output" + '/' + "confusionmatrix.png")

    print("Exporting table") 
    combined_csv.to_csv("output" + "/" + name_of_table + "_" + str(sampsize) +\
                        "samples_.csv", index = False, encoding = 'utf-8-sig') 
    print("-" * 80)
    print("Done!")
    print("-- Processing time --")
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print(
        "{:0>2}:{:0>2}:{:05.2f}".format(
            int(hours),
            int(minutes),
            seconds))


if __name__ == "__main__":
    main()

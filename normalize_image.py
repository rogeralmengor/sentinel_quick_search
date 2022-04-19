import sys 
import os 
import numpy as np 
import tqdm 
from tqdm import tqdm
import gdal 
from pprint import pprint 
import time 


__help__ = """ 
Normalizes an image that is scaled between 0 to positive values 
to -1 to 1
Parameters: 
-------------
1. CompletePath to directory with images 

Note:
-----
The output will have the same input's name with the extension 
_norm.tif

"""


def main(): 
    if len(sys.argv) < 2: 
        print(__help__)
        sys.exit(1) 

    imgs_path = sys.argv[1]
    print("--List of images to process --")
    images = [os.path.join(root, filename) for root, subdirs, filenames in os.walk(imgs_path)\
            for filename in filenames if filename.endswith(".tif")]
    pprint(images)
    
    for image in images: 
        start = time.time() 
        print(f"--Opening source image {image}--")
        src = gdal.Open(image)
        print(f"--Fetching band--")
        band = src.GetRasterBand(1)
        print(f"--Reading band as array--")
        array = src.ReadAsArray()
        print(f"--Getting maximum value of array--")
        max_val = np.nanmax(array) 
        print(f"--Getting minimum value of array--")
        min_val = np.nanmin(array)
        print(f"--Scaling array [-1, 1]--")
        scaled_array = np.array((2*((array - min_val)/(max_val - min_val))) - 1)
        print(f"--Creating output name--")
        output_img = image.replace(".tif", "_norm.tif")
        print(f"--Getting output data driver--")
        driver = gdal.GetDriverByName("GTiff")
        print(f"--Creating output image")
        dst = driver.Create(output_img, xsize=band.XSize, ysize = band.YSize,
                                    bands=1, eType=gdal.GDT_Float32)
        print(f"--Setting projection--")
        dst.SetProjection(src.GetProjection())
        print(f"--Setting GeoTransform--")
        dst.SetGeoTransform(src.GetGeoTransform())
        print(f"--Writing output array in dst file--")
        dst.GetRasterBand(1).WriteArray(scaled_array)
        proc_time = time.time() - start 
        print(f"Done! processing time: {proc_time} s --\n")
    

if __name__ == "__main__": 
    main() 

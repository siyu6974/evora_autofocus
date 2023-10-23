import numpy as np
from astropy.io import fits
import sys
import shutil
import os


def rename_file(directory, old_name, new_name):
    # Construct the full file paths for the old and new names
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)

    # Rename the file
    shutil.move(old_path, new_path)
    print(f"Renamed '{old_name}' to '{new_name}'.")

filename = sys.argv[1]
hdul = fits.open(filename)
h = hdul[0].header
image_data = hdul[0].data

seq_nb = filename.split("/")[-1].split("-")[-1].split(".")[0]
temp = h["TEMP"]
filter_exp = h["FILTER"]
exp_time = h["EXP_TIME"]
date_obs = h["DATE-OBS"].split(".")[0]
new_name = f"{date_obs}_{filter_exp}_{temp}_{exp_time}s_{seq_nb}.fits"
print(new_name)
hdu = fits.PrimaryHDU(data=image_data.astype(np.uint16))
new_name = new_name.replace(":", "-")
hdu.writeto(new_name)
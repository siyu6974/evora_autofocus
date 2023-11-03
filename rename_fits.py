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


for filepath in sys.argv[1:]:
    hdul = fits.open(filepath)
    h = hdul[0].header
    image_data = hdul[0].data

    directory = os.path.dirname(filepath)
    seq_nb = os.path.basename(filepath).split("-")[-1].split(".")[0]
    temp = h["CCD-TEMP"]
    filter_exp = h["FILTER"]
    exp_time = h["EXPTIME"]
    date_obs = h["DATE-OBS"].split(".")[0]
    new_name = f"{date_obs}_{filter_exp}_{temp}_{exp_time}s_{seq_nb}.fits"
    new_name = new_name.replace(":", "-")
    print(new_name)
    new_path = f"{directory}/{new_name}"

    hdu = fits.PrimaryHDU(data=image_data, header=h)
    hdu.writeto(new_path)

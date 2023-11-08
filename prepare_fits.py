import numpy as np
from astropy.io import fits
import sys
import shutil
import os
from astrometry_utils import extract_sources, solve, solver
import argparse

parser = argparse.ArgumentParser(description='Rename the FITS files to be more descriptive. Also add WCS information to the FITS headers.')
parser.add_argument('-s', '--solve', action='store_true', default=False, help='Solve the image and add WCS information to the FITS header.') 
parser.add_argument('-p', '--plot', action='store_true', default=False, help='Plot the sources found by SEP.') 
parser.add_argument('filenames', type=str, nargs='+', help='The filenames of the FITS files to be renamed.')       

args = parser.parse_args()


for filepath in args.filenames:
    hdul = fits.open(filepath)
    h = hdul[0].header
    image_data = hdul[0].data

    directory = os.path.dirname(filepath)
    seq_nb = os.path.basename(filepath).split("-")[-1].split(".")[0]
    temp = h.get("CCD-TEMP", "unknown_temp")
    filter_exp = h.get("FILTER", "unknown_filter")
    exp_time = h.get("EXPTIME", "unknown_exp_time")
    date_obs = h.get("DATE-OBS", "unknown_date_obs").split(".")[0]
    new_name = f"{date_obs}_{filter_exp}_{temp}_{exp_time}s_{seq_nb}.fits"
    new_name = new_name.replace(":", "-")

    if args.solve:
        wcs = None
        stars_xy = extract_sources(hdul[0].data.astype(np.float32), plot=args.plot)
        solution = solve(solver, stars_xy)
        if solution.has_match():
            print(f"{solution.best_match().center_ra_deg=}")
            print(f"{solution.best_match().center_dec_deg=}")
            
            best_match = solution.best_match()
            wcs = best_match.astropy_wcs()
        else:
            print("No match found.")

        if wcs is not None:
            wcs_header = wcs.to_header()
            h += wcs_header
        else:
            new_name = f"_{new_name}"

    print(new_name)
    new_path = f"{directory}/{new_name}"
    
    hdu = fits.PrimaryHDU(data=image_data, header=h)
    hdu.writeto(new_path)

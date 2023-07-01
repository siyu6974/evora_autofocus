import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
from astropy.visualization import AsinhStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
from photutils.centroids import centroid_quadratic
from photutils.profiles import RadialProfile

import time
import sys

APERTURE_R = 5.0


def calc_hfd(data, bg, aperture):
    total_flux = aperture_photometry(data - bg, aperture)['aperture_sum'][0]

    mask = aperture.to_mask(method='center')
    roi_data = mask.cutout(data - bg)
    dist_weighted_flux = 0
    for (y, x), pix in np.ndenumerate(roi_data):
        dist = np.sqrt(y*y+x*x)
        if dist < APERTURE_R:
            dist_weighted_flux += pix * dist
    return dist_weighted_flux / total_flux * 2


annotions = []
fig = plt.figure(figsize=(10, 8))

data = np.zeros((1024, 1024))
# im = plt.imshow(data, cmap='gist_gray_r', vmin=0, vmax=1)
ax = fig.add_subplot(111)
# plt.colorbar(label='Intensity')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Image with FWHM and HFD Annotations')

# import random
# import glob
# img_dir = "/Volumes/Backdrive 4T/astro_photo_raw/2023-05-27 MRO/evora/m57"
# images = glob.glob(f"{img_dir}/*.fits")

def main_loop():
    fits_file_url = "http://localhost:8080/data/ecam/temp.fits"
    # fits_file_url = random.choice(images)
    hdul = fits.open(fits_file_url, cache=False)
    # Load the FITS file
    # print(hdul[0].header)
    data = hdul[0].data

    # Calculate background statistics
    mean, median, std = sigma_clipped_stats(data)

    # Define the star finder parameters
    threshold = 1  # Adjust the threshold as needed
    fwhm = 5  # Adjust the FWHM as needed
    daofind = DAOStarFinder(
        fwhm=fwhm, threshold=threshold, brightest=3, sky=mean, exclude_border=True)

    # Find stars in the data
    sources = daofind(data - median)

    positions = np.transpose(
        (sources['xcentroid'], sources['ycentroid']))
    apertures = CircularAperture(positions, r=15.0)
    norm = ImageNormalize(stretch=AsinhStretch())
    # fig = plt.figure(figsize=(10, 8))  # Adjust the width (10) and height (8) as desired
    # plt.imshow(data, cmap='Greys', origin='lower', norm=norm,
    #        interpolation='nearest')
    # apertures.plot(color='blue', lw=1.5, alpha=0.5);

    # Extract the x and y coordinates of the detected stars
    x_coords = sources['xcentroid']
    y_coords = sources['ycentroid']

    # Calculate the FWHM for each detected star
    fwhm_values = []
    hfd_values = []
    
    for x, y in zip(x_coords, y_coords):
        xycen = centroid_quadratic(data, xpeak=x, ypeak=y)
        # print(data[int(x), int(y)])  # need to check if the star is not saturated
        edge_radii = np.arange(25)
        rp = RadialProfile(data - median, xycen, edge_radii, mask=None)
        fwhm_value = rp.gaussian_fwhm
        fwhm_values.append(fwhm_value)

        # HFD
        aperture = CircularAperture((x, y), r=APERTURE_R)
        hfd = calc_hfd(data, median, aperture)
        hfd_values.append(hfd)

    # Plot the image and FWHM annotations
    ax.imshow(data, cmap='gray', origin='lower', norm=norm)
    for ann in annotions:
        ann.remove()
    annotions.clear()
    # Add FWHM annotations
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        fwhm_value = fwhm_values[i]
        an = ax.annotate(f"FWHM = {fwhm_value:.2f}",
                            xy=(x, y), xycoords='data',
                            xytext=(-50, 10), textcoords='offset points',
                            arrowprops=dict(
                                arrowstyle="->", color='white'),
                            color='white')
        annotions.append(an)

    # Add HFD annotations
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        hfd_value = hfd_values[i]
        an = ax.annotate(f"HFD = {hfd_value:.2f}",
                            xy=(x, y), xycoords='data',
                            xytext=(-50, -30), textcoords='offset points',
                            arrowprops=dict(
                                arrowstyle="->", color='white'),
                            color='white')
        annotions.append(an)

    fig.canvas.draw()
    fig.canvas.flush_events()

    plt.show(block=False)
    print(f"FWHM: {hfd_values} \
        HFD: {hfd_values}")

def main():
    while True:
        try:
            main_loop()
            time.sleep(0.5)

        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print(sys.exc_info())


if __name__ == "__main__":
    main()

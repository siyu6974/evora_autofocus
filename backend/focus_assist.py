import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import io

def extract_source(data):
    # Calculate background statistics
    mean, median, std = sigma_clipped_stats(data)
    signal = data - median

    # Define the star finder parameters
    threshold = std*3  # Adjust the threshold as needed
    fwhm = 5  # Adjust the FWHM as needed
    brightest_stars = 10  # Number of stars to find
    daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold, brightest=brightest_stars, sky=mean, exclude_border=True)

    # Find stars in the data
    sources = daofind(signal)
    return sources, signal


def plot_aperature(data, aperture):
    mask = aperture.to_mask(method='center')
    roi_data = mask.cutout(data)
    plt.imshow(roi_data, cmap='Greys', origin='lower')
    plt.colorbar(label='Intensity')
    plt.show()


from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
from photutils.centroids import centroid_quadratic
from photutils.profiles import RadialProfile

APERTURE_R = 10

def calc_hfd(signal, aperture):
    mask = aperture.to_mask(method='center')
    roi_data = mask.cutout(signal)
    dist_weighted_flux = 0
    for (y, x), pix in np.ndenumerate(roi_data):
        dist = np.sqrt(y*y+x*x)
        if dist < APERTURE_R:
            dist_weighted_flux += pix * dist

    # total_flux = aperture_photometry(signal, aperture)['aperture_sum'][0]
    total_flux = np.sum(roi_data)
    return dist_weighted_flux / total_flux * 2

def calc_fwhm(signal, aperture):
    xycen = aperture.positions
    edge_radii = np.arange(25)
    rp = RadialProfile(signal, xycen, edge_radii, mask=None)
    fwhm_value = rp.gaussian_fwhm
    # plot_aperature(signal, rp.apertures[-1])
    return fwhm_value


def find_focus_position(focuser_positions, fwhm_curve_dp, hfd_curve_dp, plot=False):
        # fit the data with a quadratic
    fwhm_fit = np.polyfit(focuser_positions, fwhm_curve_dp, 2)

    # predict the minimum value
    fwhm_min_value = -fwhm_fit[1] / (2 * fwhm_fit[0])

    print(f"FWHM predicted focuser position is {fwhm_min_value:.2f}")

    # fit the data with a quadratic
    hfd_fit = np.polyfit(focuser_positions, hfd_curve_dp, 2)

    # predict the minimum value
    hfd_min_value = -hfd_fit[1] / (2 * hfd_fit[0])

    print(f"HFD predicted focuser position is {hfd_min_value:.2f}")

    image_data = None
    if plot:
        image_data_value = plot_fit(focuser_positions, fwhm_curve_dp, hfd_curve_dp, fwhm_fit, hfd_fit)

    return fwhm_min_value, hfd_min_value, image_data_value


def plot_fit(focuser_positions, fwhm_curve_dp, hfd_curve_dp, fwhm_fit, hfd_fit):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    x_fit = np.linspace(min(focuser_positions), max(focuser_positions), 100)

    # plot FWHM curve and fit
    ax1.plot(focuser_positions, fwhm_curve_dp, 'o')
    y_fit = np.polyval(fwhm_fit, x_fit)
    ax1.plot(x_fit, y_fit, label='Fit')
    ax1.set_ylabel('FWHM (pixels)')
    ax1.set_title('Focus vs FWHM')

    # plot HFD curve and fit
    ax2.plot(focuser_positions, hfd_curve_dp, 'o')
    y_fit = np.polyval(hfd_fit, x_fit)
    ax2.plot(x_fit, y_fit, label='Fit')
    ax2.set_xlabel('Focus position')
    ax2.set_ylabel('HFD (pixels)')
    ax2.set_title('Focus vs HFD')

    # mark the minimum value of the fit
    fwhm_min_value = -fwhm_fit[1] / (2 * fwhm_fit[0])
    ax1.axvline(fwhm_min_value, color='r', linestyle='--', label=f'Minimum FWHM: {fwhm_min_value:.2f}')

    hfd_min_value = -hfd_fit[1] / (2 * hfd_fit[0])
    ax2.axvline(hfd_min_value, color='r', linestyle='--', label=f'Minimum HFD: {hfd_min_value:.2f}')

    ax1.legend()
    ax2.legend()
    plt.tight_layout()

    image_data = io.BytesIO()
    plt.savefig(image_data, format='png')
    image_data_value = image_data.getvalue()
    image_data.close()
    return image_data_value
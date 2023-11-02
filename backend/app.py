from flask import Flask, request
from flask_cors import CORS
from flask import send_file
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for

from astropy.io import fits
from focus_assist import extract_source, calc_hfd, calc_fwhm, APERTURE_R, find_focus_position
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
import numpy as np

import random
from glob import glob
import sep


app = Flask(__name__)
CORS(app)

fwhm_curve_dp = []
sep_hfd_curve_dp = []
my_hfd_curve_dp = []
phd_hfd_curve_dp = []

focuser_positons = []

@app.route('/')
def index():
    return 'Hello, World!'


from flask import Flask, jsonify, make_response, send_file
import io
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')  # turn off gui
from flask import Response

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global fwhm_curve_dp
    global sep_hfd_curve_dp
    global my_hfd_curve_dp
    global phd_hfd_curve_dp
    global focuser_positons

    hfd_curve_dps = {
        "sep": sep_hfd_curve_dp,
        "my": my_hfd_curve_dp,
        "PHD": phd_hfd_curve_dp
    }
    fwhm_min, hfd_min, image = find_focus_position(focuser_positons, fwhm_curve_dp, hfd_curve_dps, plot=True)

    payload = jsonify({
        "fwhm_min": fwhm_min, 
        "hfd_min": hfd_min
    })   

    return Response(image, mimetype='image/png')


@app.route('/api/reset', methods=['POST'])
def reset():
    global fwhm_curve_dp
    global sep_hfd_curve_dp
    global my_hfd_curve_dp
    global phd_hfd_curve_dp
    global focuser_positons
    fwhm_curve_dp = []
    hfd_curve_dp = []
    focuser_positons = []
    return jsonify({
        "fwhm_curve_dp": fwhm_curve_dp, 
        "hfd_curve_dp": hfd_curve_dp,
        "focuser_positons": focuser_positons
    })


@app.route('/api/add_focus_position', methods=['POST'])
def focus_position():
    global fwhm_curve_dp
    global sep_hfd_curve_dp
    global my_hfd_curve_dp
    global phd_hfd_curve_dp
    global focuser_positons

    data = request.get_json()
    filename = data['filename']
    focuser_position = int(data['focuserPosition'])
    focuser_positons.append(focuser_position)

    fits_file_url = "http://72.233.250.83/data/ecam/" + filename
    print(fits_file_url)
    # images = glob('/Users/siyu/Proj/evora_autofocus/focus_test/manual/*.fits')
    # fits_file_url = random.choice(images)

    hdul = fits.open(fits_file_url, cache=False)
    data = hdul[0].data
    sources, signal = extract_source(data)

    x_coords = sources['x']
    y_coords = sources['y']
    x,y = list(zip(x_coords, y_coords))[0]

    # SEP HFD
    hfrs, flag = sep.flux_radius(signal, sources['x'], sources['y'], 
                            6.*sources['a'],
                            frac=0.5, 
                            subpix=5)
    median_sep_hfd = np.median(hfrs[flag==0]) * 2
    sep_hfd_curve_dp.append(median_sep_hfd)

    # FWHM and other HFD
    fwhm_values = []
    my_hfd_values = []
    phd_hfd_values = []
    for x, y in zip(x_coords, y_coords):
        aperture = CircularAperture((x, y), r=APERTURE_R)
        fwhm_value = calc_fwhm(signal, aperture)
        fwhm_values.append(fwhm_value)

        # HFD
        my_hfd, phd_hfd = calc_hfd(signal, aperture)
        my_hfd_values.append(my_hfd)
        phd_hfd_values.append(phd_hfd)
    
    fwhm_values = np.array(fwhm_values)
    median_fwhm = np.median(fwhm_values)
    fwhm_curve_dp.append(median_fwhm)

    median_my_hfd = np.median(my_hfd_values)
    my_hfd_curve_dp.append(median_my_hfd)
    median_phd_hfd = np.median(phd_hfd_values)
    phd_hfd_curve_dp.append(median_phd_hfd)
    
    return jsonify({
        "fwhm_curve_dp": fwhm_curve_dp, 
        "sep_hfd_curve_dp": sep_hfd_curve_dp,
        "my_hfd_curve_dp": my_hfd_curve_dp,
        "phd_hfd_curve_dp": phd_hfd_curve_dp,
        "focuser_positons": focuser_positons
    })



if __name__ == '__main__':
    app.run(debug=True)

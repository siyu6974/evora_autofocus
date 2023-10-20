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

app = Flask(__name__)
CORS(app)

fwhm_curve_dp = []
hfd_curve_dp = []
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
    global hfd_curve_dp
    global focuser_positons

    fwhm_min, hfd_min, image = find_focus_position(focuser_positons, fwhm_curve_dp, hfd_curve_dp, plot=True)

    payload = jsonify({
        "fwhm_min": fwhm_min, 
        "hfd_min": hfd_min
    })   

    return Response(image, mimetype='image/png')


@app.route('/api/reset', methods=['POST'])
def reset():
    global fwhm_curve_dp
    global hfd_curve_dp
    global focuser_positons
    fwhm_curve_dp = []
    hfd_curve_dp = []
    focuser_positons = []
    return jsonify({
        "fwhm_curve_dp": fwhm_curve_dp, 
        "hfd_curve_dp": hfd_curve_dp,
        "focuser_positons": focuser_positons
    })


@app.route('/api/focus_position', methods=['POST'])
def focus_position():
    global fwhm_curve_dp
    global hfd_curve_dp
    global focuser_positons

    data = request.get_json()
    focuser_position = int(data['focuserPosition'])
    focuser_positons.append(focuser_position)

    # fits_file_url = "http://localhost:8080/data/ecam/temp.fits"
    images = glob('/Users/siyu/Proj/evora_autofocus/focus_test/manual/*.fits')
    fits_file_url = random.choice(images)

    hdul = fits.open(fits_file_url, cache=False)
    data = hdul[0].data
    sources, signal = extract_source(data)

    x_coords = sources['xcentroid']
    y_coords = sources['ycentroid']
    x,y = list(zip(x_coords, y_coords))[0]

    # Calculate the FWHM for each detected star
    fwhm_values = []
    hfd_values = []

    for x, y in zip(x_coords, y_coords):
        aperture = CircularAperture((x, y), r=APERTURE_R)
        fwhm_value = calc_fwhm(signal, aperture)
        fwhm_values.append(fwhm_value)

        # HFD
        hfd = calc_hfd(signal, aperture)
        hfd_values.append(hfd)
    
    fwhm_values = np.array(fwhm_values)
    hfd_values = np.array(hfd_values)
    mean_fwhm = np.mean(fwhm_values)
    mean_hfd = np.mean(hfd_values)
    fwhm_curve_dp.append(mean_fwhm)
    hfd_curve_dp.append(mean_hfd)
    
    return jsonify({
        "fwhm_curve_dp": fwhm_curve_dp, 
        "hfd_curve_dp": hfd_curve_dp,
        "focuser_positons": focuser_positons
    })



if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request
from flask_cors import CORS
from flask import send_file
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for

from focus_assist import find_focus_position, stat_for_image

import random
from glob import glob
import logging
logging.basicConfig(level=logging.INFO)
import settings
from models import FocusSession


app = Flask(__name__)
CORS(app)

SessionStorage: {str: FocusSession} = {}

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
    payload = request.get_json()
    sid = payload['sid']
    if sid not in SessionStorage:
        return Response(status=404)
    
    session = SessionStorage[sid]
    fwhm_metrics = session.fwhm_metrics
    focuser_positons = session.focuser_positons

    hfd_curve_dps = {
        "sep": [dp['sep'] for dp in session.hfd_metrics],
        "my": [dp['my'] for dp in session.hfd_metrics],
        "PHD": [dp['PHD'] for dp in session.hfd_metrics]
    }
    fwhm_min, hfd_min, image = find_focus_position(focuser_positons, fwhm_metrics, hfd_curve_dps, plot=True)

    rtn = jsonify({
        "fwhm_min": fwhm_min, 
        "hfd_min": hfd_min
    })   

    return Response(image, mimetype='image/png')


@app.route('/api/reset', methods=['POST'])
def reset():
    payload = request.get_json()
    sid = payload['sid']
    if sid in SessionStorage:
        del SessionStorage[sid]
    return jsonify({
    })


@app.route('/api/add_focus_position', methods=['POST'])
def focus_position():
    payload = request.get_json()
    sid = payload['sid']
    if sid not in SessionStorage:
        SessionStorage[sid] = FocusSession(id=sid)
    session = SessionStorage[sid]

    filename = payload['filename']
    focuser_position = int(payload['focuserPosition'])
    session.focuser_positons.append(focuser_position)

    logging.info(f"filename: {filename} focuser_position: {focuser_position}")

    fits_file_url = settings.BASEFILE_PATH + filename

    if settings.DEBUG:
        images = glob('/Users/siyu/Proj/evora_autofocus/focus_test/manual/*.fits')
        fits_file_url = random.choice(images)

    median_fwhm, median_sep_hfd, median_my_hfd, median_phd_hfd = stat_for_image(fits_file_url)
    session.hfd_metrics.append({
        "sep": median_sep_hfd,
        "my": median_my_hfd,
        "PHD": median_phd_hfd
    })
    session.fwhm_metrics.append(median_fwhm)
    session.files.append(filename)
    logging.info(f"median_fwhm: {median_fwhm} median_sep_hfd: {median_sep_hfd} median_my_hfd: {median_my_hfd} median_phd_hfd: {median_phd_hfd}")
    
    return jsonify(session.serialize())



if __name__ == '__main__':
    app.run(debug=True)

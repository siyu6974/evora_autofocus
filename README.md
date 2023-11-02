# TODO

- Check NINA implementation for R^2 of the fit
- Show HFD and FWHM in the arcsec

# Installation

- Make sure DEBUG is set to False in `settings.py`
- Install the requirements with `pip install -r requirements.txt`

# Usage (version 0.2)

0. start the backend with `flask --app backend.app run -p 5678`, and the frontend with `npm start`

1. Take an exposure with evora

2. Put the focuser positon in the textbox and send it the backend

2.1 The backend will fetch the image from evora

2.2 The backend will process the image and return the HFD and FWHM

3. Repeat step 1 and 2 while adjusting the focuser position

4. Hit analyze to get the best focus position
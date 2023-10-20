# TODO

- Check NINA implementation for R^2 of the fit
- Subpixel HFD / interpolation
- Show HFD and FWHM in the arcsec

# Usage (version 0.1, awful architecture I know :D)

1. Take an exposure with evora
2. Put the focuser positon in the textbox and send it the backend
2.1 The backend will fetch the image from evora
2.2 The backend will process the image and return the HFD and FWHM
3. Repeat step 1 and 2 while adjusting the focuser position
4. Hit analyze to get the best focus position
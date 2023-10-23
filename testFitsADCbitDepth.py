from astropy.io import fits
import sys
# get string from command line
filename = sys.argv[1]
# Open the raw image file
hdul = fits.open(filename, cache=False)
raw_data = hdul[0].data

# Count the number of distinct values in the raw image data
vals = set(raw_data.flatten())
num_distinct_values = len(vals)

# Print the result
print(f'The number of distinct values in the raw image is: {num_distinct_values}')

# find min and max values
min_value = raw_data.min()
max_value = raw_data.max()
print(f'The minimum value in the raw image is: {min_value}')
print(f'The maximum value in the raw image is: {max_value}')

# find min difference between values in vals
vals = sorted(vals)
min_diff = vals[1] - vals[0]
for i in range(1, len(vals) - 1):
    diff = vals[i + 1] - vals[i]
    if diff < min_diff:
        min_diff = diff
print(f'The minimum difference between values in the raw image is: {min_diff}')


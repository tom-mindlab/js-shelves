# -*- coding: utf-8 -*-
"""
Get the dimensions of an image

@author: Joe Hilling 2018
"""

import sys
import os
import json
from PIL import Image

# Simple function to return the image dimensions
def getImageInfo(path):
	
	if(not os.path.isfile(path)):
		raise ValueError("no such image file: " + path)

	im = Image.open(path)
	width, height = im.size

	return {
		'width' : width,
		'height' : height
	}


# Main function for image information
if __name__ == "__main__":

	args = sys.argv
	nargs = len(args)
	if(nargs < 2):
		raise ValueError("must supply a valid path to an image file")

	output = {}

	for im_idx in range(1, nargs):

		output[args[im_idx]] = getImageInfo(args[im_idx])

	print(json.dumps(output))




# -*- coding: utf-8 -*-
"""
Get the dimensions of an image

@author: Joe Hilling 2018
"""

import sys
import os
import json
from PIL import Image, ImageFilter
import numpy as np
import pandas as pd


# Load the configuration file
def loadLayoutConfiguration(path):

	if(not os.path.isfile(path)):
		raise ValueError("no such image file: " + path)

	json_data=open(path).read()
	return json.loads(json_data)



#
# Calculate the product scaling that we need to fit the desired height
#

def applyScale(image, scale):
    w = round(image.size[0]* scale)
    h = round(image.size[1] * scale)
    
    image.thumbnail((w,h), Image.ANTIALIAS)



def loadImages(paths):

	# Load in all the images into a dictionary with the filename as the key
	images = dict()

	for r_idx, row in paths.iterrows():
		path = row['image']
		im = Image.open(path)
		applyScale(im, row['scale'])
		images[path] = im

	return images



def blurImage(im, blur_radius):
	out = im.copy()
	return out.filter(ImageFilter.GaussianBlur(radius=blur_radius)) # blur the copy
        

def generateBlurs(image_dict, blur_radius):
	
	output_dict = {}
	for key, value in image_dict.items():
		output_dict[key] = blurImage(value, blur_radius)

	return output_dict


def saveImage(image, path, quality):
	fill_color='#FFF'
	background = Image.new(image.mode[:-1], image.size, fill_color)
	background.paste(image, image.split()[-1])
	image = background

	image.save(path, "JPEG", quality=quality, optimize=True)




def populateShelfImages(output_folder, variant_folder, background_image, images, blurs, layout, quality):
	
	base_idx = layout.base[0]

	# utility function
	def getImageForRow(row):
		image_path = row['image']
		return images[image_path]

	# utility function
	def getOffsetsForRow(row):
		return (row['x_position'], row['y_position'])

	# utility function
	def getBlurredImageForRow(row):
		image_path = row['image']
		return blurs[image_path]



	# Step 1. create the base image

	base_image = background_image.copy() # clone the background image

	for index, row in layout.iterrows():
		image = getImageForRow(row)
		base_image.paste(image, getOffsetsForRow(row), image)


	# save the base image
	saveImage(base_image, output_folder + '/base_' + str(base_idx)  +'.jpg', quality )
	

	# Step 2. create a template with just the non-varying images

	template_image = background_image.copy() # clone the background image

	for index, row in layout.iterrows():

		if not row['test']:
			image = getImageForRow(row)
			template_image.paste(image, getOffsetsForRow(row), image)



	# Step 3. Iterate the test items

	varying_images = layout[layout.test]

	for index, row in varying_images.iterrows():

		# Create a copy of the template
		variant = template_image.copy()

		# Paste the blur
		blur = getBlurredImageForRow(row)
		variant.paste(blur, getOffsetsForRow(row), blur)

		# Loop the non-varying images
		others = varying_images[varying_images['index'] != row['index']]

		for index_other, other_row in others.iterrows():
			image = getImageForRow(other_row)
			variant.paste(image, getOffsetsForRow(other_row), image)

		saveImage(variant, variant_folder + '/variant_' + str(base_idx) + '_' + str(index) +'.jpg', quality)




def getVariantFolder(output_folder):

	if not os.path.isdir(output_folder):
		raise Exception('output folder "' + output_folder + '" does not exist')
    
	variant_folder = output_folder + '/variants'
	if not os.path.isdir(variant_folder):
		os.makedirs(variant_folder)

	return variant_folder


# Generates the shelves
def generateShelves(configuration_path, output_folder):
	
	# make sure there is a variant subfolder of the output folder
	variant_folder = getVariantFolder(output_folder)

	specs = loadLayoutConfiguration(configuration_path)

	background_image = Image.open('../shelves/' + specs['shelf']['image'])

	# convert the layout to a dataframe for ease of use in python
	df = pd.DataFrame.from_dict(specs['layouts'])

	# Idenitify the unique images

	# This is stupid - this information should be handed over
	scale_paths = df.groupby(['image','scale']).size().reset_index().rename(columns={0:'count'})

	# load the images
	images = loadImages(scale_paths)

	# generate the blurs
	blurs = generateBlurs(images, specs['configuration']['blur_radius'])

	quality = specs['configuration']['output_quality']

	base_indices = df.base.unique()

	for b_idx in base_indices:

		# extract the particular shelf layout
		shelf_layout = df[df.base==b_idx].reset_index(drop=True)

		# to draw the shelf we need the images the layout and the information about the shelf
		populateShelfImages(output_folder, variant_folder, background_image, images, blurs, shelf_layout, quality)

	
















# Main function for image information
if __name__ == "__main__":

	args = sys.argv
	nargs = len(args)
	if(nargs < 2):
		raise ValueError("must supply a valid path to a layout file")

	configuration_path = args[1]
	output_folder = args[2]
	

	generateShelves(configuration_path, output_folder)





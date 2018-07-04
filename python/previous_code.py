# -*- coding: utf-8 -*-
"""
Created on July 2016

@author: Jake Gale 2016
"""
from PIL import Image, ImageFilter
import pandas as pd
import random as rn
import math, os, json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#
# 
# --------------

# HERE WE CAN DEFINE WHETHER WE WANT TO BLUR THE IMAGES, CHANGE THEIR SIZES, DESATURATE, etc.
IM_BLUR = True
BLUR_RADIUS = 4

IM_DESATURATE = False
DESAT_FACTOR = 0.5

IM_RESIZE = False
RESIZE_FACTOR = 1.1

# we don't want a full GUI, so keep the root window from appearing
Tk().withdraw()
LAYOUT_FILE = askopenfilename(initialdir=os.getcwd(), title="Please select layout file")
#LAYOUT_FILE                 = 'layout.csv'
SHELF_TYPE                  = 'single'
OUTPUT_IMAGE_DIRECTORY      = 'output/images/'
OUTPUT_POSITIONS_DIRECTORY  = 'output/positions/'

if not os.path.isdir(OUTPUT_IMAGE_DIRECTORY):
    os.makedirs(OUTPUT_IMAGE_DIRECTORY)

if not os.path.isdir(OUTPUT_POSITIONS_DIRECTORY):
    os.makedirs(OUTPUT_POSITIONS_DIRECTORY)

# SHELF PROPERTIES

# define shelf_id if you know which shelf you want, else specify properties below

SHELF_ID                    = "double_std"          #"double_std"  - if you dont have a shelf in mind, let SHELF_ID = None
N_SHELVES                   = 2
WIDTH_CLASS                 = "short"

PCT_SHELF_HEIGHT            = .9            # The maximum amount of the shelf height the image can occupy

IMAGES_DIR                  = 'images/'     # must remember the /

no_rows = 3
__3D = 'n'
if __3D.lower() == 'y':
    __3D__                      = True
    no_rows = input("How many rows would you like? ( < 3): ")
    try:
        no_rows = int(no_rows)
    except ValueError:
        sys.exit("Please enter a number, %s is not a number" %no_rows)
    if no_rows > 3:
        sys.exit("%i is too large a number, please enter one less than 3" %no_rows)

elif __3D.lower() == 'n':
    __3D__                      = False
else:
    __3D = input("answer not recognised, exiting program...")
    sys.exit()


ROWS_3D                     = no_rows

# Set this to true if you are using images with price tags below
LABELS                      = False


# Load the layouts file
df                          = pd.read_csv(LAYOUT_FILE, index_col=False)


#
# Get information about the shelf image that we want to work with
# ---------------------------------------------------------------

# Load in the shelf metadata
# THIS SHOULD BE DONE THROUGH JSON OBJECTS 

with open('resources/shelf_data.json') as dataFile:
    shelf_data              = json.load(dataFile)

if SHELF_ID is not None:   
    shelf_info              = shelf_data['shelves'][SHELF_ID]
    
else: 
    for shelf in shelf_data['shelves']:
        if shelf_data['shelves'][shelf]['nShelves'] == str(N_SHELVES) and shelf_data['shelves'][shelf]['widthClass'] == WIDTH_CLASS:
            shelf_info = shelf_data['shelves'][shelf]
            break

try:
    shelf_info_test         = shelf_info
except NameError:
    print('shelf_info has not been defined, please check specified shelf properties')        
        
shelf_base              = []
shelf_heights           = []
shelf_width             = []
xOffsets1               = []
workingShelfWidth       = []
tdBacks                 = []
     
# extract shelf information
nShelves = int(shelf_info['nShelves'])
shelf_file = shelf_info['fileName']

for n in range(0,nShelves):
    shelf = shelf_info      ['shelfCoords'][n]
    shelf_base.append       (int(shelf['bottom']    ))
    shelf_heights.append    (int(shelf['bottom']    ) -int(shelf['top']))
    shelf_width.append      (int(shelf['width']     ))
    xOffsets1.append        (int(shelf['xOffset']   )-40)
    
    # td backs shows how many pixels the up of the shelf is, this is helpful when making 3D shelves
    tdBacks.append          (int(shelf_base[n] - shelf['3dBack']))
    workingShelfWidth.append(shelf_width[n] - 2 * xOffsets1[n]  )
    

    
# Load in the shelf image
shelf_image = Image.open    ('resources/' + shelf_file)


# take the smallest shelf to be the working shelf height
shelf_height                = shelf_heights[0]

for value in shelf_heights:
    shelf_height            =  min(value, shelf_height)





# -------------------------------------------------------------------------------------------------------------
#
# Load in the images specified in the layout file
# -----------------------------------------------

# Build the path to the images
df['path']                  = IMAGES_DIR + df['image']

# Load in the individual product images - dont want duplicates here
kf                          = df.drop_duplicates(['image','path'])

# Load in all the images into a dictionary with the filename as the key
images = dict()

for index, row in kf.iterrows():
    im = Image.open(row.path)
    images[row['image']]    = im


#
# Calculate the dimensions of all the product
#

# Loop through getting the image dimensions
max_height_raw              = 0

for im in images.values():
    max_height_raw = max(im.size[1], max_height_raw)
    

# SHELF INFORMATION
# ==========================================================
scaling                     = shelf_height*PCT_SHELF_HEIGHT / max_height_raw
max_height                  = math.ceil(max_height_raw *scaling)

# now that scaling has been established we can work out how far to put down labeled images
if(LABELS):
    for m in range(len(shelf_base)):
        shelf_base[m]       = shelf_base[m]+(int(240*scaling))


# Here we will randomly sample the images, and see if they fit within the shelf widths

# ==================================================================================================
# take the first base of images and work with this
# remove any duplicates
# randomly sample from the unique images, then remove it from this list

# how many of these are in the original list, multiply their width by this number

# how much remaining space is there. If the number of images can fit in this remaining space, add them to a list
# else move on to the next group
#
# =================================open================================================================


def randomizeProducts(dataframe, base):
    imageInfo           = []
    baseFrame           = dataframe[dataframe.base == base]  
    baseList            = list(baseFrame['image']) 
    
    jf                  = baseFrame.drop_duplicates(['image','path'])
    jf                  = (list(jf.index),list(jf['image']),list(jf['weights']), list(jf['blur']))


# to randomly sample, with weights, create a cumulative list of the weights
# e.g. [1,2,3,4,55,57,58,59,90] etc
# randomly sample between the min and max of these values. If the number is between two numbers, 
# the one we choose is the larger of the two numbers. We then remove this from the list and repeat      

    cumWeightList       = [0]
    cumWeight           =  0    
    blur                = [ ]
    
    for weight in jf[2]:
        cumWeight       += weight
        cumWeightList.append(cumWeight)
    
    for product in range(len(jf[0])):      
        randomInt       = rn.randint(0,cumWeightList[-1]-1)        
   
        for i,value in enumerate(cumWeightList):

            # jf[0][1][2][3] = jf[index][imageName][weights][blur]

            if randomInt < value:#
                index  = jf[0][i-1]
                chosen = jf[1][i-1]
                blur   = jf[3][i-1]
                
                # remove these values, and recalculate cumWeight#
                del      jf[0][i-1]
                del      jf[1][i-1]
                del      jf[2][i-1]
                del      jf[3][i-1]
                
                cumWeightList   = [0]
                cumWeight       = 0    

                for weight in jf[2]:
                    cumWeight   += weight
                    cumWeightList.append(cumWeight)
                break

#       How many times does this image appear in the original list, to calculate multiplicity
#       n is an arbitrary counter 
        n = 0      
        for imag in range(len(baseList)):
            if baseList[imag] == chosen:
                n+=1
                
        imageInfo.append((chosen,images[chosen].size[0],n,index, blur))

     
    return imageInfo
 
def getImageSizes(dataframe):
    
    df = dataframe.copy()
    df['size'] = 0
    for index, image in df.iterrows():
        df.loc[index,'size'] = images[df.loc[index,'image']].size[0]
                
    return df

    
     
# generate the shelf layout of the images

def generateShelf(imageInfo, base):   
    chosenImages        = []
    shelfWidths         = []
    totalImageWidth     = 0
    shelfNum            = 1   
     
# How many, if any, images won't be included in the shelf list
# =======================================================================================
    """
    for info in imageInfo:
        totalImageWidth +=info[2]*info[1]
    """
    
    for index, info in imageInfo.iterrows():
        totalImageWidth += imageInfo['size'][index]
                
    # add n elements for n shelves to be added to
    for i in range(0, nShelves):
        chosenImages.append([])    
        shelfWidths.append([])
    
    shelfWidth                  = workingShelfWidth[shelfNum-1]    
    remainingImageWidth         = shelfWidth  
    uniqueImageInfo             = imageInfo.drop_duplicates('image')

    
    #for each element in the list of images, find their width, and see where they will fit on the shelves    
    
    
    for index, file in uniqueImageInfo.iterrows():
        multiWidth              =  0
        multiplicity            =  0
        imageMultiplicityInfo   =  imageInfo[imageInfo.image == file.image]
        
        for j, subImage in imageMultiplicityInfo.iterrows():
            multiWidth          += subImage['size']
            multiplicity        += 1
        
        width                   =  multiWidth #file['size']
        remainingImageWidth     -= width

        if remainingImageWidth  < 0:
            shelfNum            += 1
            remainingImageWidth = shelfWidth-width
            
        if shelfNum <= nShelves:
            for m in range(0,multiplicity):
                chosenImages[shelfNum-1].append((file['image'],file['position'],file['size'], file['blur']))    
        
        elif shelfNum > nShelves:
            break
            
    for i in range(0,nShelves):
        # sort the images into the original order the layout defines
        chosenImages[i] = sorted(chosenImages[i], key=lambda x: x[1])  
        
    return chosenImages


#
# Calculate the product scaling that we need to fit the desired height
#

def applyScale(image, scale):
    w = round(image.size[0]* scale)
    h = round(image.size[1] * scale)
    
    return image.thumbnail((w,h), Image.ANTIALIAS)



# Apply the scaling to each of the images
for im in images.values():
    applyScale(im, scaling)

#
# START BUILDING THE SHELF IMAGES
#

# Loop the unique base images - this is the distinct layouts - not the variants
base_indices = list(df.base.unique())

#shelf_image_width = shelf_image.size[0]

# Loop over creating the images
master = None

for bIdx in base_indices:
    
    #imageInfo = randomizeProducts(df,bIdx)    
    imageInfo = getImageSizes(df[df.base == bIdx])
    shelfInfo = generateShelf(imageInfo, bIdx)
    shelfList = shelfInfo.copy()
    
    
    for i in range(0,nShelves):
        shelfList[i]    = [j[0] for j in shelfInfo[i]]
    
    # If we have all our information like this, when we convert to a dataframe at the end, it will auto-column all the information
       
    # Store the positions of each product (perhaps using total width here does not matter)
    shelves             = []
    shelf_positions     = []
    image_names         = []


    #   initialize the first values of the form:      
    #   positions = [name, shelfNumber, x1,x2,y1,y2]
    #   
    #   calculate the positions of each of the images and write to a csv for making configs   
    
    positions           = []
    yPosition           = []
    offsets             = []
    tops                = []
    
    for shelfNumber in range(0,nShelves):
        shelfPosition   = 0
        
        totalImageWidth = 0        
        
        for shelf in shelfInfo[shelfNumber]:
            totalImageWidth += shelf[2]
        
         
        # Create n number of empty containers for n shelves
        shelfPaste      = (Image.new("RGBA", (workingShelfWidth[shelfNumber], max_height), (0,0,0,0)))
        shelf_positions.append([])
        
        xOffset         = int(math.floor(shelf_image.size[0] - totalImageWidth)/2) # Center horizontal
        yPosition.append    (shelf_base[shelfNumber] - max_height) # Position vertical
        
         # Keep track of the location of the strip on the main image
        offsets.append      (xOffset)
        tops.append         (yPosition[shelfNumber])           
        
        x1 = offsets[shelfNumber]
        # work through each of the images, append their information to a list, and 
        # paste them on the blank shelf image defined above
        
        for image in shelfInfo[shelfNumber]:
            if image[0] in list(images.keys()):
                
                workingImage        = images[image[0]]
                workingImageSize    = workingImage.size
                y1                  = max_height - workingImage.size[1] + tops[shelfNumber]
                x2                  = x1 + workingImageSize[0]
                
                positions.append((image[0], shelfNumber, shelfPosition, x1, x2, y1, max_height+tops[shelfNumber], image[3]))
                
                # paste the images, but without the offsets added before
                shelfPaste.paste    (workingImage,(x1-offsets[shelfNumber],y1-tops[shelfNumber]),workingImage)    
      
                
                x1                  = x2
                shelfPosition       +=1
        
#       append these shelves to an array so all shelf images are in the same place        
        shelves.append(shelfPaste)            
                
                
    
      
    
#   Create a copy of the shelf image
    currentShelf = shelf_image.copy()
    
#   Paste the shelfs onto the background image

    for i in range(0, nShelves):
            
        if not __3D__:
            currentShelf.paste(shelves[i], (offsets[i], yPosition[i]), shelves[i]) # Paste
       
    
        else:
            # we need to have ROWS_3D number of shelves going back on each shelf
            # first let's work out how much we reduce each image by:
         
            # in the future I want to use coordinates of a shelf instead of a %, it will make it much easier to do.
            # the X iteration should be a % of the total width too.
            
            # I reckon lets hard code some values in first. 5% smaller should work, the x and y offsets are hard coded too
            # These should definitely be made a bit more dynamic
            
            TDscale         =  0.98
            shelfWidth      =  shelves[i].size[0]
            imageWidth      =  shelf_image.size[0] - offsets[i]
            
            posIterX        =  int(shelfWidth* (1-TDscale)*1.5/3)
            posIterY        =  int(tdBacks[i]/3)
            offsets[i]      += posIterX * ROWS_3D 
            yPosition[i]    -= posIterY * ROWS_3D          
            rowCount        =  ROWS_3D
            
            for j in range(0,ROWS_3D):      
                workingShelf = shelves[i].copy()
                
                for k in range (0,rowCount-1):
                    applyScale(workingShelf, TDscale) 
                    
                rowCount        -= 1
                offsets[i]      -= posIterX
                yPosition[i]    += posIterY
                currentShelf.paste(workingShelf, (offsets[i], yPosition[i]), workingShelf)
     
  


   
    positionDf = pd.DataFrame(positions, columns = ['name', 'shelfNumber', 'shelfPosition','x1','x2','y1','y2','blur'])  
      
    currentShelf.save(OUTPUT_IMAGE_DIRECTORY + 'base_' + str(bIdx) + '.png')  
    positionDf.to_csv(OUTPUT_POSITIONS_DIRECTORY + 'base_' + str(bIdx) + '.csv', index=False) 
    print('saved base: ' +  str(bIdx) )     
    blurredDf = positionDf[positionDf.blur]
    
    imageIndex = 0
    for index, row in blurredDf.iterrows():
        
        # Duplicate the background
        variant = currentShelf.copy()
        
        # get the positions of the image we want to blur
        shelfId = blurredDf.shelfNumber[index]
        shelfPosition = blurredDf.shelfPosition[index]
        X1Position = blurredDf.x1[index]
        Y1Position = blurredDf.y1[index]
        
        

        
        eIm = images[shelfList[shelfId][shelfPosition]].copy()        
        
        if IM_BLUR == True:
            if not os.path.exists(OUTPUT_IMAGE_DIRECTORY+"BLURS/"):
                os.makedirs(OUTPUT_IMAGE_DIRECTORY+"BLURS/")            
            
             # copy the clean image
            bIm = eIm.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS)) # blur the copy
        
            variant.paste(bIm, (X1Position,Y1Position), bIm) # paste this blurred image on top of the clean one        
            variant.save(OUTPUT_IMAGE_DIRECTORY +'BLURS/' + 'variant_' +str(bIdx)+'_'+str(imageIndex) + '_' + blurredDf.name[index])
            
            
        if IM_DESATURATE == True:
            
            if not os.path.exists(OUTPUT_IMAGE_DIRECTORY+"DESATS/"):
                os.makedirs(OUTPUT_IMAGE_DIRECTORY+"DESATS/")
              
            dIm = eIm.copy()
            dIm = dIm.point(lambda p:p*DESAT_FACTOR)
            
            variant.paste(dIm, (X1Position, Y1Position), dIm)
            variant.save(OUTPUT_IMAGE_DIRECTORY +'DESATS/' + 'DESATURATED_variant_' +str(bIdx)+'_'+str(imageIndex) + '_' + blurredDf.name[index])
               
               
        if IM_RESIZE == True:
            
            if not os.path.exists(OUTPUT_IMAGE_DIRECTORY+"RESIZES/"):
                os.makedirs(OUTPUT_IMAGE_DIRECTORY+"RESIZES/")
    
            originalSize = eIm.size
              
            rIm = eIm.copy()
            rIm = rIm.resize((int(rIm.size[0]*RESIZE_FACTOR), int(rIm.size[1]*RESIZE_FACTOR)), Image.ANTIALIAS)
            newSize = rIm.size
            
            # to paste it we need to find the new difference in height and width
            xDiff = newSize[0]-originalSize[0]
            yDiff = newSize[1]-originalSize[1]

            variant.paste(rIm, (int(X1Position-xDiff/2), Y1Position-yDiff), rIm)
            variant.save(OUTPUT_IMAGE_DIRECTORY +'RESIZES/' + 'RESIZED_variant_' +str(bIdx)+'_'+str(imageIndex) + '_' + blurredDf.name[index])
        
                   
     
        
        imageIndex += 1


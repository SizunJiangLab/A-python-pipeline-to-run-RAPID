import os
import sys

#####################################
# Parse command line arguments
#####################################
# Parse options. If opts is empty, it is equivalent to FALSE.

opts = [opt for opt in sys.argv[1:] if opt.startswith('-')]

if opts:
    ALTERNATIVE_OUTPUT = True
else:
    ALTERNATIVE_OUTPUT = False

try:
    PATH = sys.argv[1]
    COLUMNS = sys.argv[2]
    ROWS = sys.argv[3]
    VENV_PYTHON = sys.argv[4]
    OMETIFF_PATH = sys.argv[5]
except IndexError:
    raise SystemExit(f"Please input the following arguments.\
        \n Usage: {sys.argv[0]} <PATH> <COLUMNS> <ROWS> <VENV_PYTHON> <OMETIFF_PATH>\
        \n <PATH> : Path to the directory with raw images you want to process. \
        \n <COLUMNS> : Number of columns you want in the final OMETiff - Calculate this according to the number of regions captured. \
        \n <ROWS> : Number of rows you want in the final OMETiff - Calculate this according to the number of regions captured. \
        \n <VENV_PYTHON>: The path to the python executable. \
        \n <OMETIFF_PATH>: The path to your generate_ome_tiff.py.")

# the only parameters you have to change are these five
EXP_DIR = str(sys.argv[1]+'/')

columns = int(sys.argv[2])

rows = int(sys.argv[3])

venv_python = str(sys.argv[4])

OMETiff_path = str(sys.argv[5])

# Load JSON file
file_full_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_full_path)

import json

# exp details
with open(EXP_DIR+'experiment.json', 'r') as f:
    exp_data = json.load(f)

nCyc=exp_data['numCycles']
nReg=exp_data['numRegions']
nZ = exp_data['numZPlanes']
nTilRow = exp_data['regionHeight']
nTilCol = exp_data['regionWidth']
overlapRatio = exp_data['tileOverlapX']*100

#exposure time
with open(EXP_DIR+'exposure_times.txt', 'r') as file:
    texp=str()
    line_num = 0
    for line in file:
        line_num += 1
        if (line_num != 1):
            texp=texp+line

# Indicate path
path_input=EXP_DIR.replace("/",'\\')
path_output=path_input+"RAPID_processed\\"


###################### RAPID in Matlab #########################
import matlab.engine

# Start Matlab engine
eng = matlab.engine.start_matlab()

# Call Matlab function with input arguments
out1 = eng.RAPID_function(nCyc, nReg, nZ, nTilRow, nTilCol, overlapRatio, path_input, path_output)

# Stop Matlab engine
eng.quit()

##################### Extract channels ##########################
from skimage.io import imread, imsave, imshow
import pandas as pd
from genericpath import exists
from joblib import Parallel, delayed
from tqdm.notebook import tqdm

EXTRACT_IMG_DIR = EXP_DIR+'RAPID_processed/bestFocus/fullSizeMontage'
EXTRACT_OUT_DIR = EXP_DIR+'RAPID_processed/RAPID_Extracted'

if not exists(EXTRACT_OUT_DIR):
    os.mkdir(EXTRACT_OUT_DIR)

stack_channels = pd.read_csv(EXP_DIR+'channelNames.txt', header=None)
stack_channels = stack_channels.replace('/', '_', regex=True)

reg_tif_names = [file.name for file in os.scandir(EXTRACT_IMG_DIR)]


def extract_channels(region, channel_txt):
    reg_name = region.split('_')[0]
    # If the output directory for that region does not exist, make directory
    if not exists(os.path.join(EXTRACT_OUT_DIR, reg_name)):
        os.mkdir(os.path.join(EXTRACT_OUT_DIR, reg_name))
    # Set out path
    out_path = os.path.join(EXTRACT_OUT_DIR, reg_name) + '/'
    # Read the hyperstack tif for that region
    tif = imread(os.path.join(EXTRACT_IMG_DIR, region))
    # Get total cycle number
    CYCLE_N = tif.shape[0]
    # Get Image height
    img_height = tif.shape[1]
    # Get Image width
    img_width = tif.shape[2]
    # Get channel number
    CHANNEL_N = tif.shape[3]
    # Iterate through all the cycle and channels in each cycle
    for cycle in range(CYCLE_N):
        for channel in range(CHANNEL_N):
            # Extract image for channel j in cycle i
            img = tif[cycle, :, :, channel]
            # Get channel index corresponding to row number in the channelNames.txt
            channel_index = 4 * cycle + channel
            # Get channel name
            channel_name = channel_txt.iloc[channel_index, 0]
            # Write image
            #out_img_name = reg_name + '_' + str(cycle + 1) + '_' + channel_name + '_' + str(channel + 1) + '.tiff'
            out_img_name = channel_name + '.tiff'
            imsave(out_path + out_img_name, img, check_contrast=False)


def extract_hyperstack(img_dir, channel_txt, n_core):
    region_list = [file.name for file in os.scandir(EXTRACT_IMG_DIR)]
    stack_channels = pd.read_csv(channel_txt, header=None)
    stack_channels = stack_channels.replace('/', '_', regex=True)
    Parallel(n_jobs=n_core)(delayed(extract_channels)(region, stack_channels) for region in tqdm(region_list))


extract_hyperstack(EXTRACT_IMG_DIR, EXP_DIR+'channelNames.txt', 10)

################## Stitch TMA ###################
if nReg>1:

    from PIL import Image
    import re
    import numpy as np

    def get_subdirectories(dir):
        return [f.path for f in os.scandir(dir) if f.is_dir()]

    # >>>>> CHANGE PATH HERE where you have the tiff folders
    img_folders = get_subdirectories(EXTRACT_OUT_DIR)

    # sorter for alphanumeric order
    def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(data, key=alphanum_key)

    # sort folders in alphanumeric order so that regions are stitched to TMA in order
    img_folders = sorted_alphanumeric(img_folders)
    total_folders=len(img_folders)

    # read in desired channels
    # ASSUMES that tiff files are named directly after the channels
    # >>>>> CHANGE PATH HERE
    stack_channels_origin = pd.read_csv(EXP_DIR + 'channelNames.txt', header=None)
    unique_names = stack_channels_origin[0].unique()
    stack_channels = pd.DataFrame({'Name': unique_names})
    stack_channels = stack_channels.replace('/', '_', regex=True)
    total_stack_channels = len(stack_channels)

    # For each channel, create a new image of the TMA
    # >>>>> CHANGE AS NEEDED
    margins = 100

    tif = imread(os.path.join(EXTRACT_IMG_DIR, "reg001_montage.tif"))
    # Get Image height
    img_height = tif.shape[1]
    # Get Image width
    img_width = tif.shape[2]


    total_width = img_width*columns + (columns+1)*margins
    total_height = img_height*rows + (rows+1)*margins

    STITCH_OUT_DIR = EXP_DIR+'RAPID_processed/RAPID_Stitch'

    if not exists(STITCH_OUT_DIR):
        os.mkdir(STITCH_OUT_DIR)

    # loop through channels to stitch together TMA
    for k in range(total_stack_channels):
        # obtain channel name
        # >>>>> MIGHT BE DIFFERENT PER FILE
        channel_name = stack_channels['Name'][k]

        # create a blank grid, change size (width, height) as needed
        # Change file type to 'I;16' for 16-bit; need to also change Image open line
        new_im = Image.new('I;16', (total_width, total_height))

        # initialize index; this keeps track of the folders of the images
        folder_index = 0


        # skip function initialization
        # >>>>> INPUT LOCATIONS OF IMAGES YOU WANT SKIPPED IN TMA
        #skip_index = [62,64,65]     # input indices of the images in the full TMA that you want to skip
        #for elem in range(len(skip_index)):
        #    skip_index[elem] -=1
        image_index = 0     # this indexes the full TMA image grid; some will be skipped


        # Iterate through rows.
        for i in range(margins, total_height, img_height+margins):
            # Iterate through columns.
            for j in range(margins, total_width, img_width+margins):
                # stop the iteration when reach the last folder
                if folder_index == total_folders:
                    break
                # Skip missing images in the TMA via the skip_index
                #if image_index in skip_index:
                #    image_index +=1
                #    continue

                # read the {index}-th image
                # >>>>> CHANGE PATH HERE
                im = Image.fromarray(np.array(Image.open(img_folders[folder_index]+'/'+channel_name+'.tiff')).astype('uint16'))
                # paste at (j,i)
                new_im.paste(im, (j,i))
                # advance counters
                folder_index += 1
                image_index += 1


        # save stitched image and include channel name
        # >>>>> CHANGE NAMES HERE
        new_im.save(STITCH_OUT_DIR+"/"+channel_name+'.tiff')

####################### Make OmeTIFF ####################
import subprocess

command = venv_python + " "+OMETiff_path+" "+STITCH_OUT_DIR+" 0.38 0.38 8 -o"+EXP_DIR+"RAPID_processed/RAPID" #You need to specify the path to 'generate_ome_tiff.py'. This will create a 8 bit OMETiff

subprocess.run(command, shell=True)
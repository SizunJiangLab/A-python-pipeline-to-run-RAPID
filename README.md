# A-python-pipeline-to-run-RAPID

This script is created as a pipeline for running RAPID to deconvolve large-scale, high-dimensional fluorescence imaging data, stitch and register images with axial and lateral drift correction, and minimize tissue autofluorescence such as that introduced by erythrocytes, and do some post-processed actions to finally generate a OMETiff for visualization. 

## Software and Library Version
* `Python 3.9.6`
* `Matlab R2022a`
* `tifffile 2022.5.4`
* `Matlab engine 9.13.7`

## Dependencies and Contributions
* `RAPID` A Real-time, GPU-Accelerated Parallelized Image processing software for large-scale multiplexed fluorescence microscopy Data.
[nolanlab/RAPID](https://github.com/nolanlab/RAPID)
* `OME-TIFF Generator` [SizunJiangLab/OME-TIFF_Generator, by Huaying Qiu](https://github.com/SizunJiangLab/OME-TIFF_Generator)
* All other codes in the pipeline are generated in Sizun Lab. Thanks to Andrew Ma for help.

## File preparations
Set up the `Matlab` and `Python` environment for running `RAPID` and `tifffile` before running this pipeline.

Put your raw high-plex images and files (experiment.json, channelNames.txt, exposure_times.txt) describing experimental details in a same folder. If you use "/" when you name the channels in your run, open the 

Particularly, the structure of the folder as well as the naming of the subfolders and images should be exactly like this:
* cyc001_reg001
  * 1.bcf
  * 1_00001_Z001_CH1.tif
  * 1_00001_Z001_CH2.tif
  * 1_00001_Z001_CH3.tif
  * 1_00001_Z001_CH4.tif
  * .....
  * 1_00009_Z006_CH1.tif
  * 1_00009_Z006_CH2.tif
  * 1_00009_Z006_CH3.tif
  * 1_00009_Z006_CH4.tif

![Naming instruction](https://user-images.githubusercontent.com/57729689/187006381-9b6ef337-849d-4277-be88-bebde8718680.PNG)

**Please be noted that a standard CODEX Data Transfer will create this folder for you so it is highly recommended.**

## Usage
This script should be run as follows:
`python RAPID_pipeline.py <PATH> <COLUMNS> <ROWS> <VENV_PYTHON> <OMETIFF_PATH>`

For each argument,
* `<PATH>` Path to the directory with raw images you want to process.
* `<COLUMNS>` Number of columns you want in the final OMETiff - Calculate this according to the number of regions captured. If you have only one region, input 1.
* `<ROWS>` Number of rows you want in the final OMETiff - Calculate this according to the number of regions captured. If you have only one region, input 1.
* `<VENV_PYTHON>` The path to the python executable.
* `<OMETIFF_PATH>` The path to your generate_ome_tiff.py.

The output files will be in the same directory of your raw images.

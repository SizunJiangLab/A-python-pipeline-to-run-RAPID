# A-python-pipeline-to-run-RAPID

This script is created as a pipeline for running RAPID to deconvolve large-scale, high-dimensional fluorescence imaging data, stitch and register images with axial and lateral drift correction, and minimize tissue autofluorescence such as that introduced by erythrocytes, and do some post-processed actions to finally generate a OMETiff for visualization. 

## Software and Library Version
* `Python 3.9.6`
* `Matlab R2022a`
* `tifffile 2022.5.4`
* `Matlab engine 9.13.7`

## Reference and Dependent library
* `RAPID` A Real-time, GPU-Accelerated Parallelized Image processing software for large-scale multiplexed fluorescence microscopy Data.
[nolanlab/RAPID](https://github.com/nolanlab/RAPID)
* `OME-TIFF Generator` [SizunJiangLab/OME-TIFF_Generator](https://github.com/SizunJiangLab/OME-TIFF_Generator)
* All other codes are generated in Sizun Lab. Thanks to Andrew Ma for help

## Usage
Set up the `Matlab` and `Python` environment for running `RAPID` and `tifffile` before running this pipeline.

Put your raw high-plex images and files (experiment.json, channelNames.txt, exposure_times.txt) describing experimental details in a same folder.

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

**A standard CODEX Data Transfer will create this folder for you**

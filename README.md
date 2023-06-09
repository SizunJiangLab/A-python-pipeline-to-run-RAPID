# A-python-pipeline-to-run-RAPID

This script is created as a pipeline for running RAPID to deconvolve large-scale, high-dimensional fluorescence imaging data, stitch and register images with axial and lateral drift correction, and minimize tissue autofluorescence such as that introduced by erythrocytes, and do some post-processed actions to stitch all the regions and generate a OMETiff for visualization. 

## Software and Library Version
* `Python 3.9.6`
* `Matlab R2022a`
* `tifffile 2022.5.4`
* `Matlab engine 9.13.7`

## Dependencies and Contributions
* `RAPID` A Real-time, GPU-Accelerated Parallelized Image processing software for large-scale multiplexed fluorescence microscopy Data.
[nolanlab/RAPID](https://github.com/nolanlab/RAPID)
* `OME-TIFF Generator` [SizunJiangLab/OME-TIFF_Generator, by Huaying Qiu](https://github.com/SizunJiangLab/OME-TIFF_Generator)

## File preparations
Set up the `Matlab` and `Python` environment for running `RAPID` and `tifffile` before running this pipeline. Place the scripts in `src` in the same folder with your RAPID library. Set the mjipath, ijpath and pluginpath in RAPID_function.m to your local path.

Prepare your raw high-plex images and files (experiment.json, channelNames.txt, exposure_times.txt) describing experimental details in a folder.

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

Here's an example of running this pipeline:

**In your command line tool/terminal:**

`python /Users/GuanruiLiao/JiangLab/RAPID_processing/RAPID_pipeline_publish.py /Users/GuanruiLiao/JiangLab/data/Cancer 5 5 /Users/ServerRight/.conda/envs/RAPID_processing/python.exe /Users/GuanruiLiao/JiangLab/generate_ome_tiff.py`

The output files will be in the same directory of your raw images， including:
* Main folder - RAPID_processed
  * Subfolder - RAPID_extracted: includes seperate images of every channel in all the regions
  * (If you have more than one region) Subfolder - RAPID_stitch: includes seperate images of every channel with all the regions stitched together
  * RAPID.ome.tiff: The final Tiff file with all the channels and regions combined

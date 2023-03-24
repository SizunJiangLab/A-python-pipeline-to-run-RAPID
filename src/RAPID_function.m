function output=RAPID_function(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8)
% Example to run RAPID
% Guolan Lu, Aug 2022


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% set up the following path
% specify the directory of raw data
path_input = arg7;

% specify directory of processed data
path_output = arg8;

% specify directory of PSF
path_psf = 'D:\RAPID_processing\PSF\PSF\';

% specify path for using imageJ within matlab
mjipath = 'C:\Program Files\MATLAB\R2022b\java\mij.jar';
ijpath = 'C:\Program Files\MATLAB\R2022b\java\ij.jar';
pluginpath = 'C:\Users\ServerRight\Desktop\Fiji.app\plugins\';

%% Change the following parameters for each experiment
im_row = 1440; im_col = 1920; % define the image size of each tile; 20x

nCyc = arg1; % number of cycles
nReg = arg2; % number of regions
nZ = arg3; % number of z stacks
nTilRow = arg4; % number of row tiles
nTilCol = arg5; % number of column tiles
overlapRatio = arg6; % microscope overlapping ratio in precentage

nCh = 1:4; % filter channels
nTil = nTilRow*nTilCol; % number of tiles
reg_range = 1:nReg; % the range of regions to process
cyc_range = 1:nCyc; % the range of cycles to process

til_range = 1:nTil; % the range of titles to process

cpu_num = 5; % number of CPU workers to use for parallel computing
neg_flag = 1; % set to 1 means: make negative values after bg subtraction zeros
gpu_id = 1;  % set the id of GPU as 1 or 2 (two GPUs in this computer)

% specify background cycle to subtract
cyc_bg = 1;

% exposure time table
texp = dlmread(strcat(path_input, 'exposure_times.txt'), ',', 1, 0);

% image acquisition mode: multipoint or memopoint
mode = 'memopoint';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Don't change the following code
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
parpool(cpu_num)
% ------------------------------------------------------------------------
%% Module 1:
%  - decovolution
%  - identify the best focus plane (axial drift compensation)
% tic
disp('Start deconvolution...');
deconv_par(reg_range, cyc_range, til_range, nZ, path_input, path_output, path_psf,im_row,im_col,nCh,mode,gpu_id)
disp('Deconvolution done...');
% toc

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Module 2: lateral drift compensation
% ------------------------------------------------------------------------
%% stitch individual tiles: within-cycle lateral drift compensation
% tic
if nTil >1
    disp('Start stitching...');
   
    MIST_stitch(mjipath,ijpath,pluginpath,path_output,reg_range,cyc_range,nTilCol,nTilRow,overlapRatio);

    makeMosaic(path_output,reg_range,cyc_range);
    
    disp('Stitching done...');
end
% toc


% ------------------------------------------------------------------------
%% between-cycle lateral drift compensation:

% tic
disp('Start drift compensation...');
driftCompensate_par(reg_range,cyc_range,path_output,nCh,nTil,gpu_id);
% driftCompensate(reg_range,cyc_range,path_output,cpu_num,nCh,nTil);
disp('Drift compensation done...');
% toc

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Module 3:
% -------------------------------------------------------------------------
% subtract background cycle
% tic
disp('Start background subtraction...');
if nTil>1
    margin = 12;
elseif nTil == 1
    margin = 0;
end
rowFinal = im_row*nTilRow - im_row*(overlapRatio/100)*(nTilRow-1) + margin;
colFinal = im_col*nTilCol - im_col*(overlapRatio/100)*(nTilCol-1) + margin;

bgSubtract_par(reg_range,cyc_range,texp,cyc_bg,path_output,neg_flag,rowFinal,colFinal,nCh);
% bgSubtract(reg_range,cyc_range,texp,cyc_bg,path_output,neg_flag,cpu_num,rowFinal,colFinal,nCh); % Elapsed time is 76.505625 seconds.
% bgSubtractRBC(reg_range,cyc_range,texp,cyc_bg,path_output,neg_flag,cpu_num,rowFinal,colFinal,nCh); % remove strong autofluorescence

disp('Background subtraction done...');
% toc


% ------------------------------------------------------------------------
%% concentenate all the stacks into a hyperstack
% tic
disp('Start concatenation...');
genHyperstack(reg_range, cyc_range, path_output,nCyc,nCh,im_row, im_col, mjipath,ijpath,pluginpath)
disp('Concatenation done...');
% toc
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
delete(gcp('nocreate'));
output=1
end

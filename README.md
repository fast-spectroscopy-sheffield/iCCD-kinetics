## Splice Together Kinetic Data from the iCCD

This app allows you to join together kinetic traces from the iCCD to create a single kinetic trace. Files to load should be the original .asc files created by the batch conversion tool from Andor. Aquisition info, if included, must be appended to the bottom of the files rather than the top. There must be __at least one time point common to both files at each join__.

#### Installation and Requirements

App has only been tested on Windows 10. The app requires python 3. Recommended installation through Miniconda. Miniconda can be downloaded [here](https://conda.io/miniconda.html).

Once python is installed you should download the repository to your computer. You will need to create a python environment to run the app in, containing the required packages. To do this open an admin anaconda prompt and `cd` your way to the folder where you downloaded the repository and run
```
conda env create -f environment.yml
```
This file is a little outdated now - the app will run fine with latest versions of all the packages listed in the environment file. The app can then be launched as follows. First open an anaconda prompt. If using the environment, you will need to activate it first:
```
conda activate iccd-kinetics-env
```
Then `cd` your way to the folder where you downloaded the python code and run
```
python app.py
```

#### Instructions for Use

Launch the app. If you want to apply the spectral sensitivity correction, load the appropriate calibration file using the browse button.

Next, load the initial kinetic, which should include the time zero point, by pressing the browse button adjacent to the first line entry. Choose the file, then enter the start time and gate step by double clicking the three dashes in the appropriate boxes. If you want to also upload a background file for this first kinetic, uncheck the tick box.

Load the rest of the kinetic files by pressing browse next to the larger box. You will be prompted to load a file and straight afterwards, the corresponding background file. For each file, enter the start time and gate step as before. You can change the order of the files using the move up and move down buttons. Files can be deleted using delete.

Once you are happy with the file list, and all files are in the correct order, press load. You must choose the correct delimiter before pressing load. If you don't the program will crash when you try to add the time axis.

Next, adjust the value of time zero in the appropriate box and press add time axes. The timeslices and kinetics plots should become populated by data from the __first kinetic file only__.

If you want to, press remove cosmic rays. Algorithm is not perfect and needs some work, it reduces rather than removes the spikes.

Use the slider below the timeslices graph to move through the timepoints. Select an appropriate background end point (not relevant if a background file was supplied for the first kinetic) and press subtract backgrounds.

Finally, press join.

If you loaded a calibration file, you can apply the calibration.

You can now visualise the joined kinetic using the two graphs, save the data using the two save buttons, and reset the app using the red reset button in order to load a new set of files.

#### Known Issues

There is a problem with screen resolutions for the GUI. If the GUI looks weird on your screen, please let me know and I'll try to fix it for you.

For **backgrounds**, in the lab, if a 'Kinetic' is taken instead of 'Accumulate', it will only use the first 'column' in the background kinetic series for background subtraction. Basically taking 'Kinetic' instead of 'Accumulate' is presently a waste of lab time. Maybe background-averaging or by-column-background-subtration needs implementing into the code.
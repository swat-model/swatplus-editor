By default, we typically ship SWAT+ Editor with three versions of the model: the official stable release, the latest development version, and the previous model release version.
If you would like to provide your own SWAT+ model version, you may copy your executable files into this folder, then open the exe-options.csv file and add a new row with the description and file name of your custom executable.

Caution: providing your own executables may cause errors if it is not compatible with the editor's default official release version. 
Changes in input or output file formats between model versions may cause errors.

Want to run the model outside of SWAT+ Editor? In this version the .dll files in this folder are required, so if you just copy and paste the .exe file, you will encounter errors if you don't have Fortran installed. 
Instead, open a command prompt. Navigate to your TxtInOut folder (cd "C:\My-Project\Scenarios\Default\TxtInOut"), then run the SWAT exe providing the full path name. 

In the command prompt from inside your TxtInOut, type something like: "C:\Users\{YOUR_USERNAME}\SWATPlus\SWATPlusEditor\resources\app.asar.unpacked\static\swat_exe\{EXE_FILENAME_TO_RUN}.exe"
Remember to adjust the above for your full path and SWAT exe revision number.
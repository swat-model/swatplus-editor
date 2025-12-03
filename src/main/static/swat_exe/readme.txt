You may update the model run in SWAT+ editor by replacing the files in this directory. Please note the following:

1. File names must be exactly the same, OR
2. Update the version number in the appsettings.json file in the directory above this one. If the version number in that file is updated, the SWAT+ exe file names must match accordingly.

Want to run the model outside of SWAT+ Editor? In this version the .dll files in this folder are required, so if you just copy and paste the .exe file, you will encounter errors if you don't have Fortran installed. 
Instead, open a command prompt. Navigate to your TxtInOut folder (cd "C:\My-Project\Scenarios\Default\TxtInOut"), then run the SWAT exe providing the full path name. 

In the command prompt from inside your TxtInOut, type something like: "C:\Users\{YOUR_USERNAME}\SWATPlus\SWATPlusEditor\resources\app.asar.unpacked\static\swat_exe\rev{CURRENT_VERSION}_64rel.exe"
Remember to adjust the above for your full path and SWAT exe revision number.
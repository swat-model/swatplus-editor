### SWAT+ Editor 3.2.0 ###

* Add option to choose model revision to run
  * Comes with official current, latest development, and previous release versions
  * Allow user to more easily add their own executable
* Re-work output file analysis to read .csv instead of .txt files and auto-populate all tables
  * Added advanced option for skipping specified files in the interface
* Re-work project update function and separate datasets DB updating for easier management in the future
* Change 'Slice' to 'none/barren' in the land use pie chart on the project setup screen
* Remove option to create weather station manually; added more warning/instruction on manual edit screen
* Include [pull request #24](https://github.com/swat-model/swatplus-editor/pull/24): add netcdf climate preparation to api
  * Netcdf with SWAT+ requires a model version update that will be released at a later time
* Include [pull request #25](https://github.com/swat-model/swatplus-editor/pull/25): gwflow bypass floodplain if channel ID not found

_No breaking changes from v3.0.0 and later._
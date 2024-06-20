* Release 3.0.0.
* We recommend users please visit the SWAT+ website to update your QSWAT+ version
* SWAT+ model update to revision 61.0
  * See [model release notes](https://swatplus.gitbook.io/docs/release-notes) for a full list of changes
* Added editor interfaces for groundwater flow module (GWFLOW):
  * Requires initial model setup using GWFLOW option in the latest QSWAT+
  * Found in the editor under Connection -> Groundwater Flow
* Updated model support for constituents:
  * Fixed bugs in file format for pest/path_hru/water.ini files
  * Updated interface to simplify enabling and adding pesticides and pathogens
  * Added new salinity module and interfaces
* Updated the soft calibration interfaces and functionality
* Some menu reorganization:
  * Move plant communities udner Land Use Management
  * Rename Initialization to Constituents
* Add the ability to choose which model input text files to write or not write
  * Under the Run page, expand 'Choose where to write your input files' and click the 'Advanced: Customize files to write' button
* Add a link to the model executable folder in the Run page so you can more easily update the model if neeeded
  * On the Run page, click the folder icon to the right of the model version number
* Underlying code framework updates:
  * Update python rest API code to link to the project database in the request header
  * No longer use python flask restful package and just use the main flask to serve the API
  * Update to Vue.js 3.x
  * Change from Bootstrap Vue to Vuetify GUI framework
* Various bug fixes and GUI enhancements

View the full list of changes at swat.tamu.edu/software/plus
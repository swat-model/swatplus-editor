# Change Log #

## Version 3 ##

### Revision 3.0.3 ###

* Update tiledrain.str dist parameter default to 5m; users should manually update their project values if using tile drains
* Bug fix in hard calibration and other pages where it wasn't allowing negative numbers
* Bug fix in adding outflow to point source / inlets
* Minor package updates
* Add automatic software updates

### Revision 3.0.2 ###

* Change default of codes.bsn i_fpwet from 2 to 1 due to model issue in rev. 61.0.1
* Bug fix in landuse management editor where Manning's N dropdown was using CN2 values
* Bug fix in SWAT+ Check dark mode theme where text on images was not visible
* Added 'More Actions...' buttons to the Run and SWAT+ Check pages for easier navigation 

### Revision 3.0.1 ###

* SWAT+ model update to revision 61.0.1
  * See [model release notes](https://swatplus.gitbook.io/docs/release-notes) for a full list of changes
* Bug fix: check for old version of swatplus_datasets.sqlite in new projects
* SWAT+ Check and GWFLOW are not fully compatible at this time. Added a fix so that you can still run SWAT+ Check, but with a warning about some missing values in the hydrology and landscape nitrogen losses sections.
* Bug fix: gwflow_wetlands table wasn't always created by default causing an error writing inputs.

### Revision 3.0.0 ###

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
  * Move plant communities under Land Use Management
  * Rename Initialization to Constituents
* Add the ability to choose which model input text files to write or not write
  * Under the Run page, expand 'Choose where to write your input files' and click the 'Advanced: Customize files to write' button
* Add a link to the model executable folder in the Run page so you can more easily update the model if needed
  * On the Run page, click the folder icon to the right of the model version number
* Underlying code framework updates:
  * Update python rest API code to link to the project database in the request header
  * No longer use python flask restful package and just use the main flask to serve the API
  * Update to Vue.js 3.x
  * Change from Bootstrap Vue to Vuetify GUI framework
* Various bug fixes and GUI enhancements

## Version 2 ##

### Revision 2.3.3 ###

* Bug fix related to num_steps column in weir_res that should have been deleted.

### Revision 2.3.2 ###

* Bug fix when creating a new project without QGIS: invalid reference to path join.

### Revision 2.3.1 ###

* Fixed long-standing issue regarding aquifer routing. The editor was routing from aquifer to downstream channel (following through a PT in gis_routing and to the downstream channel or reservoir). Instead, we needed to take the channel/reservoir associated with the PT the aquifer routes to. So in gis_routing instead of AQU->PT->CH/RES, it should be AQU->CH/RES where CH/RES is found from AQU->PT and CH/RES->PT.

### Revision 2.3 ###

* SWAT+ model updated to revision 60.5.7; see model revision notes for input/output changes
* swatplus_datasets.sqlite updated to version 2.3
* Due to the change to plants.plt, if you're updating an existing project, consider reloading your plants database with the new data through the interface. Download the plants CSV file from plus.swat.tamu.edu (browse to version 2.3), and from SWAT+ Editor go to Edit -> Databases -> Plants, click the Import button, then select the Import tab and downloaded CSV file.
* Added basic interface for building water allocation tables. Water allocation tables are very specific to the watershed and new feature in SWAT+. We recommend working with the model development team if you are unsure. Because this is a new addition, the interface is still limited if you're trying to build a large table with many source and demand objects.
* Bug fix in SWAT+ Check - urban codes now displayed in the Land Use Summary section

### Revision 2.2.2 ###

* Bug fix for error received when enabling constituents and saving

### Revision 2.2.1 ###

* Bug fix for creating new atmospheric deposition station
* Bug fix when saving and loading scenarios

### Revision 2.2 ###

* Complete reworking of source code to update Electron and Vue.js
* Added interface for atmospheric deposition
* Added a delete all button to weather stations and weather generator pages
* HRU/Hydrology/EPCO default now set to 0.5
* Added button to project setup page to re-import from GIS and switch between full SWAT+ and SWAT+ lte
* Added link to SWAT+ Toolbox

### Revision 2.1 ###

* SWAT+ input structure update for revision 60.5.4. Please see the model release notes at the top of this page for changes.
Recall/Export Coefficients sections combined and renamed to Point Source / Inlet within the editor. Previous bugs in writing these inputs have been corrected.
* Decision table editing is now available. You may edit individual tables in plain text, and there is now a guided interface for the land use management decision tables under the Land Use Management -> Management Schedules section. Use the guided builder to select from prebuilt tables from the SWAT+ development team and edit values to suit your model. Types of decision tables available include: crop rotation, tillage, fertilizer, irrigation, grazing, hay and forest cutting.
* Observed weather data files with different starting and ending dates are now allowed through the import process. Please note that model simulation dates outside the range of your observed data will result in simulated weather.

### Revision 2.0.4 ###

* Fix bug affecting SWAT+ lte projects during input file writing.

### Revision 2.0.3 ###

* Minor update to add WETW and WETM land uses to swatplus_datasets.sqlite. WETW is for playas and WETM is not currently active. This requires you to update to QSWAT+ version 2.0.6.
* Improved write time for .con (connect) files. This mostly affects larger projects or grid models.
* Fix default location of WGN database for Linux/Mac.

### Revision 2.0.1 ###

* Minor update to fix write time of rout_unit.def and ls_unit.def for larger projects with many HRUs.

### Revision 2.0.0 ###

We recommend using new projects created in the new QSWAT+ 2.0.x with version 2 of the editor. However, if this is not feasible, an upgrade function is available when you load your older projects in the editor. If you are using the land use management (lum.dtl) default decision tables provided in previous versions of the editor, we recommend manually updating them. The old ones have an error causing crops not to be planted. Download instructions below:

Editor feature updates:

* New feature: save and load scenarios. After running the model, make a copy of your inputs and outputs. Any changes made after saving will not affect the saved scenario. Load the scenario back to the editor anytime from the project setup screen.
* New feature: SWAT+ Check. Features from SWAT Check have been brought in for SWAT+ and built in directly to the editor. This is still a work in progress.
* New feature: constituents section available under initialization data editing section. Pesticides and pathogens are available to be configured.

User interface redesigned and enhanced:

* Project setup screen simplified and project information shown here after project is loaded.
* SWAT+ lte (simplified model with just channels and HRUs) option now available for all projects when importing GIS.
* Connections editing screens simplified to combine connect file inputs and properties into one.
* Bulk editing mode now available when clicking edit on any item and using the pull down arrow on the right of the Save Changes button. Filtering available by subbasin, landuse, and HRU if applicable.
* Table views may now be filtered.
* Copy feature added to most sections (click on edit to an item). Does not apply to connection objects.
* Import from GIS functionality updated. Aquifers now read from QSWAT+ routing tables, speeding up import. Users are recommended to install the most recent QSWAT+ 2.0.x for this feature.
* Default project data updated:
* Set values for hydrology.hyd variables perco, cn3_swf, and latq_co based on soil hyd. group and HRU slope
* Project database structure and dataset updates to match revisions in SWAT+ rev. 60.5.x (see model revision notes linked in section above).

## Version 1 ##

### Revision 1.2.3 ###

* Fixed bug in reading output file headers
* Fixed bug that allowed user to run model without adding weather generator data
* Added rotation year to management operation schedule
* Updated SWAT+ rev. 59.3 to fix bug where it wasn't printing all IDs in lsunit output files

### Revision 1.2.2 ###

* Fixed bug in writing aqu_catunit.ele where basin fraction would be 0 for small areas
* Fixed various bugs while importing GIS data
* Updated model rev. 59.3 with various bug fixes
* Improved weather and wgn importing speed when matching to connect objects
* Limit map view in connect pages to avoid display locking in large projects
* When writing inputs, changed bsn_frac column to exponential format for better precision

### Revision 1.2.1 ###

* Small fix for projects using barren land use.
* Fixed bug when receiving an error trying to edit a row in landuse management.

### Revision 1.2.0 ###

* Compatible with SWAT+ rev. 59.3
* Fixes default routing in rout_unit_con for upland to floodplain surface runoff. Use fraction of area of upland routing unit surface runoff goes to channel/reservoir, the remaining goes to floodplain (see Bieger et al. JAWRA 2019). New projects only, existing projects should try re-import from GIS option. 
* Change aquifer creation. Previously created one aquifer per channel. Changed to two per subbasin (upland/floodplain), and add a deep aquifer for each outlet.
* Fixes default principal/emergency area and volume of reservoirs. Note: new projects / re-import GIS data only. Existing projects should update values manually as needed. New defaults are described below:
	* Principal spillway area (area_ps) is set from GIS data
	* Emergency spillway area is set to area_ps * 1.15
	* Principal spillway volume is set to area_ps * 10
	* Emergency spillway volume is set to area_es * 10
* Un-managed ponds are now retained as HRUs in QSWAT+. Imported to the editor as HRUs with wetlands inputs (wetlands_wet and hydrology_wet).
* Update output database tables to include revisions from model rev. 59.3: channel and channel morph, reservoir, and wetlands columns.
* Project update function available for the following data changes related to model rev. 59.1-3:
	* Update cal_parm_cal abs_max=10 and units=m for flo_min and revap_min. Add dep_bot.
	* Update aquifer_aqu default values for gw_flo=0.05, dep_wt=10, flo_min=5, revap_min=3.
	* In plant_ini_item, yrs_init changed to fraction (change values to 1 where previously 15), and biomass increased for some plants. Lc_status changed to yes for past and barr plants.
	* Update codes_bsn default values for pet=1, rtu_wq=1, wq_cha=1
* User interface improvements:
	* Add csv import for weather generator data.
	* All related table search boxes return all possible results underneath matches to typed text.
	* Add automatic database rollback when user gets an error importing GIS or updating project.
* Bug fixes:
	* Fixed bug when updating project from 1.0.0, a variable was not declared.
	* Fixed bug where weather stations were created but not always assigned weather data file if one exists.
	* Fixed bug when trying to import weather data located on another hard drive.
	* Fixed bug where swatplus_rest_api.exe wasn't terminating correctly when exiting the editor.

### Revision 1.1.1 ###

* Fixes bug when importing GIS data into plant communities not in the datasets database
* Print section usability update
* Update automatic project database backups so multiple failed import/upgrade attempts don't overwrite the original

### Revision 1.1.0 ###

* Upgrade function available for projects made with version 1.0.0.
* Compatible with SWAT+ rev. 59.
* Re-designed project setup page. If importing GIS, allow SWAT+ lte option for projects without point source or reservoir data.
* Channels now default to using the channel-lte structure (as per SWAT+ rev. 58). Please note that this means your channel input files are different (chandeg.con) and the channel output will be in channel_sd tables.
* New management schedule and decision table defaults determined by your HRU's plant type in plants.plt. It will use an automatic schedule based on corn (warm) or wheat (cold) plants. See the land use management documentation for more information.
* New editor sections for: basin parameters, connections--export coefficients, recall, delivery ratio, landscape unit regions, land use management, calibration, initialization data, soils, databases, and structural.
* Added export/import to and from CSV files for most sections.
* Other miscellaneous usability improvements.

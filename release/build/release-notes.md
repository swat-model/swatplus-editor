### SWAT+ Editor v3.0.4 ###

* SWAT+ Check bug fix - the the Land Use Summary tab, urban land use codes were not being looked up correctly resulting in 'NA'. Updated SWAT+ Check to refer to the name in landuse.lum, but this will require standard names in the form of "cropname_lum". More detailed warnings given when this naming lookup is unsuccessful.
* Added default curve number values for importing SWAT+ lte projects so users do not get errors when using custom plants outside the standard table provided by SWAT+.

_No breaking changes from v3.0.0 and later._
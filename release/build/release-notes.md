### SWAT+ Editor v3.1.2 ###

* Set minimum wd and dp in hyd-sed-lte.cha to 0.001 instead of 0.00001 due to error in values less that 0.001 introduced in 61.0.2.

### Revision 3.1.1 ###

* Bug fix where Channels -> Hydrology & Sediment and Nutrients pages were not displaying.

### Revision 3.1.0 ###

* Update to SWAT+ rev. 61.0.2
* Fix printing day_lag_max in the parameters.bsn to integer.
* Fix bug in print.prt where salts and constituents objects were duplicated.
* Remove water allocation editor because it is outdated (will rework in a future release).
* Update Basin Parameters ->  adj_pkrt_sed, set default to 484 and recommended range to 250-800.
* Update Hard Calibration / Parameters (cal_parms.cal) to remove unused parameters and non-zero minimums.

_No breaking changes from v3.0.0 and later._
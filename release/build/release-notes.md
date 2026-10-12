### SWAT+ Editor 4.1.0

- Update to SWAT+ rev. 62.0.1
- Time-series recall (point source/inlet) data is re-enabled with SWAT+ rev. 62.0.1
- Rev. 62.0.1 also fixes bug from 62.0.0 in export coefficient (constant point source) input file structure, so this functionality is also restored
- Update nutrients.res columns: chla_co -> nsolr and secchi_co -> psolr; same default values used for both (1)
- Removed unused carbon=1 option in codes.bsn drop down list
- Developer feature: update reading exe-options.csv to have Linux and MacOS specific files with fallback to default to ease compiling on these platforms

### SWAT+ Editor 4.0.2

- Bug fix affecting gfortran compiling: print plants.plt days_mat and yrs_mat as integer instead of decimals.
- Work-around fix affecting instances where the model has an error exit code despite the model running successfully.

### SWAT+ Editor 4.0.1

- Bug fix related to codes_bsn/i_fpwet column name change giving an error on new project setups using an old swatplus_datasets.sqlite version.

### SWAT+ Editor 4.0.0

- Compatible with SWAT+ rev. 62
- gwflow structure updates (QSWAT+ v4.0 update is REQUIRED)
- Add carbon module (see basin section for carbon and carbon layers)
- Update print.prt to include gwflow options and legacy carbon options
- Time-series recall DISABLED (update to 4.1.0 to re-enable)

_Several breaking changes from v3.x. This version is NOT backwards compatible._

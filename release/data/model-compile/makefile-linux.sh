#!/bin/bash 
# run the following first to set intel environment
# . ~/intel/oneapi/setvars.sh or . /opt/intel/oneapi/setvars.sh
mv scen_read_filterstrip.f90 scen_read_filterstrip.f90x
rm *.o
rm *.mod
rm rev60.5.7_64rel_linux
ifort -c hru_module.f90 -traceback -O3 -parallel
ifort -c time_module.f90 -traceback -O3 -parallel
ifort -c constituent_mass_module.f90 -traceback -O3 -parallel
ifort -c *_module.f90 -traceback -O3 -parallel
ifort -c allocate_parms.f90 -traceback -O3 -parallel
ifort -c *.f90 -traceback -O3 -parallel
ifort -o rev60.5.7_64rel_linux *.o -traceback -O3 -parallel -static

rm *.o
rm *.mod
rm rev60.5.7_64debug_linux
ifort -c hru_module.f90 -g -traceback -check all -parallel
ifort -c time_module.f90 -g -traceback -check all -parallel
ifort -c constituent_mass_module.f90 -g -traceback -check all -parallel
ifort -c *_module.f90 -g -traceback -check all -parallel
ifort -c allocate_parms.f90 -g -traceback -check all -parallel
ifort -c *.f90 -g -traceback -check all -parallel
ifort -o rev60.5.7_64debug_linux *.o -g -traceback -check all -parallel -static

chmod 755 rev60.5.7_64rel_linux
chmod 755 rev60.5.7_64debug_linux
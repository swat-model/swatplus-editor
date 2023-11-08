#!/bin/bash 
# run the following first to set intel environment
# . /opt/intel/oneapi/setvars.sh
mv scen_read_filterstrip.f90 scen_read_filterstrip.f90x
rm *.o
rm *.mod
rm rev60.5.7_64rel_mac
ifort -c hru_module.f90 -traceback -O3 -parallel
ifort -c time_module.f90 -traceback -O3 -parallel
ifort -c constituent_mass_module.f90 -traceback -O3 -parallel
ifort -c *_module.f90 -traceback -O3 -parallel
ifort -c allocate_parms.f90 -traceback -O3 -parallel
ifort -c *.f90 -traceback -O3 -parallel
ifort -o rev60.5.7_64rel_mac *.o -L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -llapack -lblas -traceback -O3 -parallel

rm *.o
rm *.mod
rm rev60.5.7_64debug_mac
ifort -c hru_module.f90 -g -traceback -check all -parallel
ifort -c time_module.f90 -g -traceback -check all -parallel
ifort -c constituent_mass_module.f90 -g -traceback -check all -parallel
ifort -c *_module.f90 -g -traceback -check all -parallel
ifort -c allocate_parms.f90 -g -traceback -check all -parallel
ifort -c *.f90 -g -traceback -check all -parallel
ifort -o rev60.5.7_64debug_mac *.o -L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -llapack -lblas -g -traceback -check all -parallel

chmod 755 rev60.5.7_64rel_mac
chmod 755 rev60.5.7_64debug_mac
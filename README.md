spival
======

spival is used to manage a Git repository that contains the latest kernels
of a given SPICE Kernel Dataset (SKD).

SPICE is an essential tool for scientists and engineers alike in the 
planetary science field for Solar System Geometry. Please visit the NAIF 
website for more details about SPICE.
 

Function and Purpose
--------------------

Auxiliary data are those that help scientists and engineers to determine the 
location and orientation of the spacecraft, when and how an instrument was 
acquiring scientific data. These data also help to determine what other 
relevant events were occurring on the spacecraft or ground that might affect 
the interpretation of the scientific observation or the S/C systems performance. 
Software applications are required to know what were the location, size, shape 
and orientation of the observed target in addition to these auxiliary data. 
Almost all NASA and ESA planetary missions have embraced the use of the SPICE 
system for ancillary data archiving and for science data analysis. Although the 
Flight Dynamics Division provides software to read the position and orientation 
files of the orbiters, most of the Principal Investigators (PI) have pointed out 
their interest in having all the auxiliary data distributed in SPICE format.

The ESA SPICE Service (ESS) of the Cross Mission Support Office is responsible 
for supporting the ESOC auxiliary data transformation into SPICE kernels and 
the distribution of these files to the instrument teams using the public network. 
NASA’s Planetary Data System discipline node NAIF (Navigational Ancillary 
Information Facility) is responsible for designing a transformation software 
tool to generate spacecraft orbit and attitude SPICE kernels. The ESS, helped 
by the individual instrument and FDy teams, the SGSs, and, in some missions, 
supported by NAIF, design and support all the necessary instrument, spacecraft 
and timing kernels.

adcsng is developed and maintained by the [ESA SPICE Service (ESS)](https://spice.esac.esa.int).


Environmental Considerations
----------------------------

spival is a Python 3.5.x package that uses a set of standard Python libraries.

Installation
------------

Then run ``pip install spival`` to install from pypi.

If you wish to install spival from source first download or clone the project. Then run ``python setup.py install``.
To uninstall run ``pip uninstall spival``.


Usage
-----

spival requires an initialised Git repository and a SPICE Kernel Dataset directory structure.


Known Working Environments:
---------------------------

spival is compatible with modern 64 bits versions of Linux and Mac.
If you run into issues with your system please submit an issue with details. 

- OS: OS X, Linux
- CPU: 64bit
- Python 3.5
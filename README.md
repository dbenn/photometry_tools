# Photometry tools

_modify-fits-header.py_ 

* This script modifies the FITS header of the supplied files in various ways, such as to correct time using a timezone offset, MIDPOINT, JD, RA, Dec, calibration status, filter, object name and so on.
 
* It also makes the FITS header minimally VPhot compliant by changing the the DATE-OBS keyword's value to be in ISO 8601 format (and removing the UT-START keyword since its value is included in the modified DATE-OBS).
 
* This script is dependent upon the astropy package. One easy way to get this is to install a scientific Python distribution such as Anaconda.
 
_zeros-and-offset.py_

* This script removes leading zeros from file names in the current directory, subtracts an optional offset value from the sequence number in each, and copies the file to a temporary directory. 

* This simple script was written for conversion of Canon (1100D) RAW file names to a form suitable for processing by IRIS batch commands such as "convertraw".

"""
Converts RA and Dec in degrees to sexagisimal format.

RA and Dec are expected to be the first and second command-line arguments.
"""

import sys

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import SkyCoord

if len(sys.argv) > 1:
    c = SkyCoord(ra=float(sys.argv[1]), dec=float(sys.argv[2]), unit='deg')
    print(c.to_string('hmsdms').replace('d', ':').replace('m', ':').replace('h', ':').replace('s', ''))

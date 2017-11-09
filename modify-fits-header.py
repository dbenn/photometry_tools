# This script modifies the FITS header of the supplied files in various ways, 
# such as to correct time using a timezone offset, MIDPOINT, JD, RA, Dec,
# calibration status, filter, object name and so on.
#
# It also makes the FITS header minimally VPhot compliant by changing the 
# the DATE-OBS keyword's value to be in ISO 8601 format (and removing the
# UT-START keyword since its value is included in the modified DATE-OBS).
#
# This script is dependent upon the astropy package. One easy way to get this 
# is to install a scientific Python distribution such as Anaconda.
#
# Nov 2014, Aug 2015 
# dbenn@computer.org
#
# Notes:
# o VPhot FITS header requirements:
#   http://184.73.185.143/app/restricted/uploading/HeaderRequirements.aspx

from astropy.time import Time, TimeDelta
from astropy.io import fits as fitsio
from optparse import OptionParser
import re

def main():
    (options, args) = get_opts_and_args()

    if len(args) >= 1:
        for arg in args:
            try:
                fits = fitsio.open(arg, mode="update")
                try:
                    optionally_set_iris_dateobs(fits, options, arg)
                    set_times(fits, options, arg)
                    set_object(fits, options, arg)
                    set_filter(fits, options, arg)
                    set_airmass(fits, options, arg)
                    set_calstat(fits, options, arg)
                    set_ra(fits, options, arg)
                    set_dec(fits, options, arg)
                except KeyError as e:
                    print("** Error: {0}".format(e))

                fits.flush()
                fits.close()
            except IOError as e:
                print("** {0}".format(e))

    else:
        parser.print_help()

def get_opts_and_args():
    global parser
    parser.add_option("-a", "--airmass",
                      action="store", dest="airmass", default=None,
                      help="Airmass value", metavar="AIRMASS")
    parser.add_option("-c", "--calstat",
                      action="store", dest="calstat", default=None,
                      help="Calibration status; one or more of B, D, F: B = bias, D = dark subtracted, F = flat fielded, e.g. B or BD or BDF", 
                      metavar="CALSTAT")
    parser.add_option("-i", "--iris-dateobs",
                      action="store", dest="iris_dateobs", default=None,
                      help="Set IRIS-style DATE-OBS (DD/MM/YYYY) from yyyy-mm-dd before other processing",
                      metavar="DATE_OBS")
    parser.add_option("-d", "--dec",
                      action="store", dest="dec", default=None,
                      help="Declination (D:M:S.n or D M S.n)", metavar="DEC")
    parser.add_option("-e", "--exptime",
                      action="store", dest="exp_time", default="0.0",
                      help="Exposure time in seconds", metavar="EXP_TIME")
    parser.add_option("-f", "--filter",
                      action="store", dest="filter", default=None,
                      help="Photometric filter", metavar="FILTER")
    parser.add_option("-m", "--use-midpoint-for-dateobs",
                      action="store_true", dest="use_midpoint_for_dateobs", 
                      default=False,
                      help="Use mid-point time (if set) for DATE-OBS")
    parser.add_option("-j", "--adjust-time",
                      action="store_true", dest="adjust_time", 
                      default=False,
                      help="Adjust time according to other time options")
    parser.add_option("-o", "--object",
                      action="store", dest="object", default=None,
                      help="Object name", metavar="OBJECT")
    parser.add_option("-r", "--ra",
                      action="store", dest="ra", default=None,
                      help="Right Ascension (H:M:S.n or H M S.n)", metavar="RA")
    parser.add_option("-t", "--tzoffset",
                      action="store", dest="tz_offset", default="0.0",
                      help="Time zone offset to add to time (in hours)", 
                      metavar="TZ_OFFSET")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose setting")

    return parser.parse_args()

def set_times(fits, options, arg):
    """
    Adjust observation time (as DATE-OBS), mid-point, JD (for midpoint).
    """
    if not options.adjust_time:
        return

    full_dateobs = extract_full_dateobs(fits, arg)

    if full_dateobs is not None:
        initial_t = Time(full_dateobs, scale='utc', format='isot')
        if options.verbose:
            print("{0}: {1} [start]".format(arg, initial_t.isot))
        
        tz_offset = float(options.tz_offset)
        tz_delta_t = TimeDelta(tz_offset*60*60, format='sec')
        adjusted_t = initial_t + tz_delta_t

        exp_time = float(options.exp_time)
        if exp_time == 0 and 'EXPTIME' in fits[0].header:
            exp_time = float(fits[0].header['EXPTIME'])

        midpoint_delta_t = TimeDelta(exp_time/2, format='sec')
        midpoint_t = adjusted_t + midpoint_delta_t

        if options.use_midpoint_for_dateobs:
            print("{0}: using midpoint for DATE-OBS".format(arg))
            new_date_obs = midpoint_t.isot
        else:
            new_date_obs = adjusted_t.isot

        fits[0].header['DATE-OBS']  = new_date_obs
        if options.verbose:
            print("{0}: {1} [adjusted]".format(arg, new_date_obs))

        fits[0].header['MIDPOINT'] = midpoint_t.isot
        if options.verbose:
            print("{0}: {1} [midpoint]".format(arg, midpoint_t.isot))

        fits[0].header['JD'] = midpoint_t.jd
        if options.verbose:
            print("{0}: {1} [JD]".format(arg, midpoint_t.jd))

def optionally_set_iris_dateobs(fits, options, arg):
    """
    Optionally set IRIS style DATE-OBS.
    """
    iris_dateobs = None

    if options.iris_dateobs is not None:
        pattern = re.compile("^\s*(\d{4})\-(\d{1,2})\-(\d{1,2})\s*$")
        match = pattern.match(options.iris_dateobs)
        if match is not None:
            iris_dateobs = "{0}/{1}/{2}".format(match.group(3).zfill(2), 
                                                match.group(2).zfill(2),
                                                match.group(1).zfill(4))     

            dateobs = None 
            if 'DATE-OBS' in fits[0].header:
                dateobs = fits[0].header['DATE-OBS']
            
            fits[0].header['DATE-OBS'] = iris_dateobs
            fits.flush()

            if options.verbose:
                print("{0}: {1} [initial]".format(arg, dateobs))
                print("{0}: {1} [adjusted]".format(arg, iris_dateobs))
        else:
            print("format of {0} not yyyy-mm-dd".format(options.iris_dateobs))

def extract_full_dateobs(fits, arg):
    """
    Attempt to extract the full observation date as an ISO 8601 date string.
    If UT-START was found, delete it, consolidating date and time in DATE-OBS. 
    """
    full_dateobs = None

    if 'UT-START' in fits[0].header and 'DATE-OBS' in fits[0].header:
        utstart = fits[0].header['UT-START']
        dateobs = fits[0].header['DATE-OBS']
        date_fields = dateobs.split("/")
        if len(date_fields) == 3:
            (dd,mm,yyyy) = date_fields
            full_dateobs = "{0}-{1}-{2}T{3}".format(yyyy, mm, dd, 
                                                    utstart)
            
            del fits[0].header['UT-START']
        else:
            print("{0}: DATE-OBS format not DD/MM/YYYY".format(arg))

    elif 'DATE-OBS' in fits[0].header:
        full_dateobs = fits[0].header['DATE-OBS']
    else:
        print("{0} does not contain DATE-OBS keyword".format(arg))

    return full_dateobs

def set_object(fits, options, arg):
    if options.object is not None:
        fits[0].header['OBJECT'] = options.object
        if options.verbose:
            print("{0}: Set object to {1}".format(arg, options.object))

def set_filter(fits, options, arg):
    if options.filter is not None:
        if 'FILTER' in fits[0].header:
            old_filter = fits[0].header['FILTER']
        else:
            old_filter = None
            fits[0].header['FILTER'] = options.filter
            if options.verbose:
                print("{0}: Filter changed from {1} to {2}".format(arg, 
                                                              old_filter, 
                                                              options.filter))
def set_airmass(fits, options, arg):
    if options.airmass is not None:
        fits[0].header['AIRMASS'] = options.airmass
        if options.verbose:
            print("{0}: Set airmass to {1}".format(arg, options.airmass))

def set_calstat(fits, options, arg):
    if options.calstat is not None:
        if options.calstat not in ["B", "BD", "BF", "DF", "BDF"]:
            print("{0}: CALSTAT must be one of B, BD, BF, DF, BDF".format(arg))
        else:
            fits[0].header['CALSTAT'] = options.calstat
            if options.verbose:
                print("{0}: Set calstat to {1}".format(arg, options.calstat))

def set_ra(fits, options, arg):
    if options.ra is not None:
        h_m_s = get_hd_m_s_str(options.ra, prefix="")
        if h_m_s is not None:
            fits[0].header['RA'] = h_m_s
            if options.verbose:
                print("{0}: Set RA to {1}".format(arg, options.ra))
        else:
            print("{0}: Invalid RA '{1}'".format(arg, options.ra))

def set_dec(fits, options, arg):
    if options.dec is not None:
        d_m_s = get_hd_m_s_str(options.dec)
        if d_m_s is not None:
            fits[0].header['DEC'] = d_m_s
            if options.verbose:
                print("{0}: Set DEC to {1}".format(arg, options.dec))
        else:
            print("{0}: Invalid DEC '{1}'".format(arg, options.dec))

def get_hd_m_s_str(input, prefix="\-|\+"):
    pattern = re.compile("^\s*(({0})?\d+):(\d+):(\d+(\.\d+)?)\s*$".format(prefix))
    match = pattern.match(input)
    hd_m_s = None
    if match is not None:
        hd_m_s = "{0} {1} {2}".format(match.group(1), 
                                      match.group(3), 
                                      match.group(4))
    return hd_m_s

if __name__ == "__main__":
    usage = "usage: %prog [options] fits-file1 fits-file2 ..."
    parser = OptionParser(usage=usage)
    main()

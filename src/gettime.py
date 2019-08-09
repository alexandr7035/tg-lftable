import pytz
import ssl
import urllib.request
from datetime import datetime


# The most important function of the program.
# Get and return timetable's mtime using urllib module.
def ttb_gettime(ttb):

    # THIS IS A HOTFIX TO PREVENT "CERTIFICATE_VERIFY_FAILED" ERROR!
    # DISABLE THIS LATER
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Request
    response =  urllib.request.urlopen(ttb.url, timeout=25, context=ctx)

    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])

    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')

    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')

    date = old_tz.localize(gmt_date).astimezone(new_tz)

    return(date)

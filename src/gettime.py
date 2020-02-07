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


# In this function we need to return both time and url (to use later in messages)
def credit_ekzam_gettime(timetable):

    # THIS IS A HOTFIX TO PREVENT "CERTIFICATE_VERIFY_FAILED" ERROR!
    # DISABLE THIS LATER
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # See src.static.py 
    # If there is winter and summer timetable files avaiable (course 1-3), get both, 
    # compare and return the freshest 
    # Else get only winter time (for course 4)

    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')

    if len(timetable.urls) == 2:
        winter_url = timetable.urls['winter']
        summer_url = timetable.urls['summer']

        # Get winter time
        response =  urllib.request.urlopen(winter_url, timeout=25, context=ctx)
        native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
        gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
        winter_date = old_tz.localize(gmt_date).astimezone(new_tz)

        # Get summer time
        response =  urllib.request.urlopen(summer_url, timeout=25, context=ctx)
        native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
        gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
        summer_date = old_tz.localize(gmt_date).astimezone(new_tz)

        # Choose relevant time and return
        if winter_date > summer_date:
            return({'time': winter_date, 'url': winter_url})
        else:
            return({'time': summer_date, 'url': summer_url})

    else:
        winter_url = timetable.urls['winter']

        # Get only winter time
        response =  urllib.request.urlopen(winter_url, timeout=25, context=ctx)
        native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
        gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
        winter_date = old_tz.localize(gmt_date).astimezone(new_tz)

        return({'time': winter_date, 'url': winter_url})
import logging
import os
from static import log_dir
import sys

# Nothing will work without logging
if not os.path.exists(log_dir):
    try:
        os.mkdir(log_dir)
    except Exception:
        print("CRITICAL ERROR: can't create log directory '" + log_dir + "'. Exit")
        sys.exit()

# A simple logger
#logging_filename = log_dir + 'lftable-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.log'
logging_filename = log_dir + 'lftable.log'

logger = logging.getLogger('lftable')
logger.setLevel(logging.DEBUG)

filehandler = logging.FileHandler(filename=logging_filename)
filehandler.setFormatter(logging.Formatter('%(filename)s [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'))
logger.addHandler(filehandler)

# Use '-e' option to start this logger
def log_exceptions():
    # Uncomment this and see 'log/lftable-exceptions.log' if something goes wrong.

    # Logger for all exceptions.
    logging.basicConfig(filename=log_dir + "lftable-exceptions.log", level=logging.DEBUG)
    exception_logger = logging.getLogger('exception_logger')

    # Install exception handler
    def my_handler(type, value, tb):
        exception_logger.exception("Uncaught exception: {0}".format(str(value)))
    sys.excepthook = my_handler

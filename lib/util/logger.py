import os
import sys
import logging


try:
    import colorlog
except ImportError:
    pass

def setup_logging(name):
    root = logging.getLogger(name)
    root.setLevel(logging.INFO)
    # following includes the module name
    # format = '%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s'
    format = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
                                      log_colors={'DEBUG': 'reset', 'INFO': 'reset',
                                                  'WARNING': 'bold_yellow', 'ERROR': 'bold_red',
                                                  'CRITICAL': 'bold_red'})
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)


setup_logging(__name__)
log = logging.getLogger(__name__)

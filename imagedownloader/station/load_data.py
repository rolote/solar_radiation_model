
from datetime import datetime
import numpy as np
import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.read("datalogger.cfg")
#section = 'CR1000_CMP11'

#print cfg.sections()

#for sec in cfg.sections():
#    print cfg.options(sec)
'''
print cfg.get(section, 'DATA_FILE')
print type( cfg.getint(section, 'TIMESTAMP_COL')) 
print cfg.getint(section, 'CHANNEL') 
print cfg.get(section, 'TIME_FORMAT')
print cfg.get('CR1000_CMP11', 'DELIMITER')
print cfg.getint('CR1000_CMP11', 'SKIP_ROWS')
'''

def get_data(section):
    data_file = cfg.get(section, 'DATA_FILE')
   # print data_file
    timestamp_col = cfg.get(section, 'TIMESTAMP_COL') 
    channel = cfg.getint(section, 'CHANNEL') 
    time_format = cfg.get(section, 'TIME_FORMAT')
#    delimiter = cfg.get(section, 'DELIMITER')
    skip_rows = cfg.getint(section, 'SKIP_ROWS')
#    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
   # def convert_timestamp(s, time_format):
    #    lambda s: datetime.striptime(s[1:20],
     #                                time_format)

    arch = np.genfromtxt(data_file, 
                          delimiter = ',',
                          skiprows= skip_rows,
                          usecols=(0, channel),
                          converters = {0: lambda s: datetime.strptime(s[1:20],
                                                                 time_format  ),
                                       channel: lambda s: float(s)}
                         )
    return arch
'''
arch= get_data('CR1000_CMP11')
for lines in arch:
    for cel in  lines:
       print cel,
    print
'''

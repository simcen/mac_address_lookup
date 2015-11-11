import sys, time
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators
import json
import urllib
import datetime
import splunk.rest as rest
import splunk.input as input    
import hashlib
import socket
import splunk
import urllib


@Configuration()
class GetMacVendor(StreamingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """

    field  = Option(require=False)

    def stream(self, records):
        #self.logger.debug('ModifyIncidentsCommand: %s', self)  # logs command line
        #user = self._input_header.get('owner')
        sessionKey = self._input_header.get('sessionKey')
        splunk.setDefault('sessionKey', sessionKey)

        self.logger.debug("Started")
        for record in records:
            
            mac_address = None

            if self.field:
            	if self.field in record:
            		mac_address = record[self.field]
            else:
            	if 'mac_address' in record:
            		mac_address = record['mac_address']

            if mac_address != None:
            
            	url = 'http://www.macvendorlookup.com/api/v2/%s' % record['mac_address']

            	try:
                	urlHandle = urllib.urlopen(url)
                	content = urlHandle.read()
                	content = json.loads(content)

                	record['mac_address_vendor'] = content[0]['company']
                	record['mac_address_vendor_country'] = content[0]['country']

                except Exception as e:
			        exc_type, exc_obj, exc_tb = sys.exc_info()
			        self.logger.error("Unable to open url %s. Reason: %s. Line: %s" % (url, exc_type, exc_tb.tb_lineno))

            else:
                self.logger.warn("No mac_address field found in event, aborting.")  

            yield record
       

dispatch(GetMacVendor, sys.argv, sys.stdin, sys.stdout, __name__)

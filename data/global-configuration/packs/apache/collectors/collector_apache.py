import traceback

from opsbro.httpclient import get_http_exceptions, httper
from opsbro.collector import Collector
from opsbro.parameters import StringParameter


class Apache(Collector):
    parameters = {
        'hostname': StringParameter(default='localhost'),
        'user'    : StringParameter(default=''),
        'password': StringParameter(default=''),
    }
    

    def __init__(self):
        super(Apache, self).__init__()
        self.apacheTotalAccesses = None
        
    
    def launch(self):
        
        if not self.is_in_group('apache'):
            self.set_not_eligible('Please add the apache group to enable this collector.')
            return
        
        logger = self.logger
        logger.debug('getApacheStatus: start')
        '''
                    passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    passwordMgr.add_password(None, self.config['apacheStatusUrl'], self.config['apacheStatusUser'],
                                             self.config['apacheStatusPass'])

                    handler = urllib2.HTTPBasicAuthHandler(passwordMgr)

                    # create "opener" (OpenerDirector instance)
                    opener = urllib2.build_opener(handler)

                    # use the opener to fetch a URL
                    opener.open(self.config['apacheStatusUrl'])

                    # Install the opener.
                    # Now all calls to urllib2.urlopen use our opener.
                    urllib2.install_opener(opener)
        '''
        try:
            uri = 'http://%s/server-status/?auto' % self.get_parameter('hostname')
            user = self.get_parameter('user')
            password = self.get_parameter('password')
            response = httper.get(uri, timeout=3,user=user, password=password)
        except get_http_exceptions() as exp:
            stack = traceback.format_exc()
            self.log = stack
            self.set_error('Unable to get Apache status - Exception = %s' % exp)
            return False
        
        logger.debug('getApacheStatus: urlopen success, start parsing')
        # Split out each line
        lines = response.split('\n')
        
        # Loop over each line and get the values
        apacheStatus = {}
        
        logger.debug('getApacheStatus: parsing, loop')
        
        # Loop through and extract the numerical values
        for line in lines:
            values = line.split(': ')
            try:
                apacheStatus[str(values[0])] = values[1]
            except IndexError:
                break
        
        logger.debug('getApacheStatus: parsed')
        
        res = {}
        
        try:
            if apacheStatus['Total Accesses'] != False:
                logger.debug('getApacheStatus: processing total accesses')
                totalAccesses = float(apacheStatus['Total Accesses'])
                if self.apacheTotalAccesses is None or self.apacheTotalAccesses <= 0 or totalAccesses <= 0:
                    res['req/s'] = 0.0
                    self.apacheTotalAccesses = totalAccesses
                    logger.debug('getApacheStatus: no cached total accesses (or totalAccesses == 0), so storing for first time / resetting stored value')
                else:
                    logger.debug('getApacheStatus: cached data exists, so calculating per sec metrics')
                    res['req/s'] = (totalAccesses - self.apacheTotalAccesses) / 60
                    self.apacheTotalAccesses = totalAccesses
            else:
                self.set_error('getApacheStatus: Total Accesses not present in mod_status output. Is ExtendedStatus enabled?')
        except (IndexError, KeyError):
            self.set_error('getApacheStatus: IndexError - Total Accesses not present in mod_status output. Is ExtendedStatus enabled?')
        
        try:
            if apacheStatus['BusyWorkers'] != False and apacheStatus['IdleWorkers'] != False:
                res['busy_workers'] = int(apacheStatus['BusyWorkers'])
                res['idle_workers'] = int(apacheStatus['IdleWorkers'])
            else:
                self.set_error('getApacheStatus: BusyWorkers/IdleWorkers not present in mod_status output. Is the URL correct (must have ?auto at the end)?')
        except (IndexError, KeyError):
            self.set_error('getApacheStatus: IndexError - BusyWorkers/IdleWorkers not present in mod_status output. Is the URL correct (must have ?auto at the end)?')
        
        return res

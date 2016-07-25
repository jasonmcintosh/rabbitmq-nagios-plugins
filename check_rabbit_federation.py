#!/usr/bin/env python
import check_rabbit_federation
from pynagios import make_option, Response, CRITICAL, OK
from base_rabbit_check import BaseRabbitCheck
import string

class RabbitCheckFederation(BaseRabbitCheck):
  """
  performs a nagios compliant check on a single queue and
  attempts to catch all errors. expected usage is with a critical threshold of 0
  """
  def makeUrl(self):
    """
    forms self.url, a correct url to polling a rabbit federation api endpoint
    """
    try:
      if self.options.use_ssl is True:
        self.url = "https://%s:%s/api/federation-links" % (self.options.hostname, self.options.port)
        return True
      else:
        self.url = "http://%s:%s/api/federation-links" % (self.options.hostname, self.options.port)
        return True
    except Exception, e:
      print str(e)
      self.rabbit_error = 3
      self.rabbit_note = "problem forming api url:", e
      return False

  def testOptions(self):
    return True

  def setPerformanceData(self, data, result):
    # for the moment there is no perfdata
    return result

  def parseResult(self, data):
    failed_repls = []
    for result in data:
      if result['status'] != 'running':
        msg = "%s %s %s %s" % ( result['node'], result['vhost'], result['exchange'], result['status'] )
        failed_repls.append(msg)

    if failed_repls:
      return Response(CRITICAL, (', '.join(failed_repls)))

    return Response(OK, "federation links are all up")

if __name__ == "__main__":
  obj = RabbitCheckFederation()
  obj.check().exit()

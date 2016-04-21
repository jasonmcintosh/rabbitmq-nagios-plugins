#!/usr/bin/env python
from pynagios import make_option
from base_rabbit_check import BaseRabbitCheck


class RabbitVhostCheck(BaseRabbitCheck):
    """
    performs a nagios compliant check on a single vhost and
    attempts to catch all errors. expected usage is with a critical threshold of 0
    """

    vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')

    def makeUrl(self):
        """
        forms self.url, a correct url to polling a rabbit vhost
        """
        try:
            if self.options.use_ssl is True:
                self.url = "https://%s:%s/api/vhosts/%s" % (self.options.hostname, self.options.port, self.options.vhost)
            else:
                self.url = "http://%s:%s/api/vhosts/%s" % (self.options.hostname, self.options.port, self.options.vhost)
            return True
        except Exception, e:
            self.rabbit_error = 3
            self.rabbit_note = "problem forming api url:", e
        return False

    def testOptions(self):
        """
        returns false if necessary options aren't present
        """
        if not self.options.hostname or not self.options.port or not self.options.vhost:
            return False
        return True

    def setPerformanceData(self, data, result):
        result.set_perf_data(self.vhost + "_messages", data['messages'])
        result.set_perf_data(self.vhost + "_rate", data['messages_details']['rate'])
        result.set_perf_data(self.vhost + "_consumers", data['consumers'])
        result.set_perf_data("rabbit_error", self.rabbit_error)
        return result

    def parseResult(self, data):
        self.vhost = self.options.vhost
        result = self.response_for_value(data['messages'])
        result.message = self.rabbit_note
        return result


if __name__ == "__main__":
    obj = RabbitVhostCheck()
    obj.check().exit()

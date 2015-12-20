#!/usr/bin/env python
from pynagios import make_option
from base_rabbit_check import BaseRabbitCheck


class RabbitQueueCheck(BaseRabbitCheck):
    """
    performs a nagios compliant check on a single queue and
    attempts to catch all errors. expected usage is with a critical threshold of 0
    """

    vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')
    queue = make_option("--queue", dest="queue", help="Name of the queue in inspect", type="string")

    def makeUrl(self):
        """
        forms self.url, a correct url to polling a rabbit queue
        """
        try:
            if self.options.use_ssl is True:
                self.url = "https://%s:%s/api/queues/%s/%s" % (self.options.hostname, self.options.port, self.options.vhost, self.options.queue)
            else:
                self.url = "http://%s:%s/api/queues/%s/%s" % (self.options.hostname, self.options.port, self.options.vhost, self.options.queue)
            return True
        except Exception, e:
            self.rabbit_error = 3
            self.rabbit_note = "problem forming api url:", e
        return False

    def testOptions(self):
        """
        returns false if necessary options aren't present
        """
        if not self.options.hostname or not self.options.port or not self.options.vhost or not self.options.queue:
            return False
        return True

    def setPerformanceData(self, data, result):
        result.set_perf_data(self.queue + "_messages", data['messages'])
        result.set_perf_data(self.queue + "_rate", data['messages_details']['rate'])
        result.set_perf_data(self.queue + "_consumers", data['consumers'])
        result.set_perf_data("rabbit_error", self.rabbit_error)
        return result

    def parseResult(self, data):
        self.queue = self.options.queue
        result = self.response_for_value(data['messages'])
        result.message = self.rabbit_note
        return result


if __name__ == "__main__":
    obj = RabbitQueueCheck()
    obj.check().exit()

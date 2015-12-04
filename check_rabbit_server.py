#!/usr/bin/env python
import string
from pynagios import make_option, Response, WARNING, CRITICAL
from base_rabbit_check import BaseRabbitCheck


class RabbitCheckServer(BaseRabbitCheck):
    """
    performs a nagios compliant check on a single queue and
    attempts to catch all errors. expected usage is with a critical threshold of 0
    """
    type = make_option("--type", dest="type", help="Type of check - mem, fd, proc, sockets, disk", type="string", default='%2F')

    def makeUrl(self):
        """
        forms self.url, a correct url to polling a rabbit queue
        """
        try:
            if self.options.use_ssl is True:
                self.url = "https://%s:%s/api/nodes" % (self.options.hostname, self.options.port)
            else:
                self.url = "http://%s:%s/api/nodes" % (self.options.hostname, self.options.port)
            return True
        except Exception, e:
            print str(e)
            self.rabbit_error = 3
            self.rabbit_note = "problem forming api url:", e
        return False

    def testOptions(self):
        if not self.options.type:
            self.rabbit_note = "Missing type"
            return False
        if not (self.options.type == 'mem' or self.options.type == 'fd' or self.options.type == 'proc' or self.options.type == 'sockets' or self.options.type == 'disk'):
            self.rabbit_note = "Type of " + self.options.type + " is incorrect"
            return False
        return True

    def setPerformanceData(self, data, result):
        result.set_perf_data(self.options.hostname + '_' + self.options.type, self.percentage)
        return result

    def parseResult(self, data):
        for result in data:
            if string.split(result['name'], '@')[1] in self.options.hostname:
                nodeData = result
        if nodeData:
            if self.options.type == 'mem':
                if nodeData['mem_alarm'] is True:
                    return Response(CRITICAL, 'memory alarm triggered!')
                self.percentage = nodeData[self.options.type + "_used"] / (nodeData[self.options.type + "_limit"] / 100.0)
            if self.options.type == 'disk':
                if nodeData['disk_free_alarm'] is True:
                    return Response(CRITICAL, 'disk alarm triggered!')
                self.percentage = nodeData[self.options.type + "_free_limit"] / (nodeData[self.options.type + "_free"] / 100.0)

            if self.options.type == 'fd':
                self.percentage = nodeData[self.options.type + "_used"] / (nodeData[self.options.type + "_total"] / 100.0)

            if self.options.type == 'proc':
                self.percentage = nodeData[self.options.type + "_used"] / (nodeData[self.options.type + "_total"] / 100.0)

            if self.options.type == 'sockets':
                self.percentage = nodeData[self.options.type + "_used"] / (nodeData[self.options.type + "_total"] / 100.0)

            return self.response_for_value(self.percentage, self.options.type + ' usage is ' + str(self.percentage) + ' used ')
        return Response(WARNING, 'No node data found!')


if __name__ == "__main__":
    obj = RabbitCheckServer()
    obj.check().exit()

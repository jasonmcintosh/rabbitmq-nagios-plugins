#!/usr/bin/env python
from pynagios import Plugin, make_option, Response, CRITICAL, UNKNOWN
from base_rabbit_check import BaseRabbitCheck
import json

class RabbitAllQueuesCheck(BaseRabbitCheck):

    vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')

    def makeUrl(self):
        """
        forms self.url, a correct url to polling a rabbit queue
        """
        try:
            if self.options.use_ssl is True:
                self.url = "https://%s:%s/api/queues/%s" % (self.options.hostname, self.options.port, self.options.vhost)
            else:
                self.url = "http://%s:%s/api/queues/%s" % (self.options.hostname, self.options.port, self.options.vhost)
            return True
        except Exception, e:
            self.rabbit_error = 3
            self.rabbit_note = "problem forming api url:", e
        return False

    def generateQueueUrl(self, queueName):
        try:
            if self.options.use_ssl is True:
                self.url = "https://%s:%s/api/queues/%s/%s" % (self.options.hostname, self.options.port, self.options.vhost, queueName)
            else:
                self.url = "http://%s:%s/api/queues/%s/%s" % (self.options.hostname, self.options.port, self.options.vhost, queueName)
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

    def parseResult(self, data):
            if data.get('messages'):
                    result = self.response_for_value(data['messages'])
                    result.message = ' found ' + str(data['messages']) + ' messages'
                    self.rabbit_note = ' found ' + str(data['messages']) + ' messages'
            else:
                    result = self.response_for_value(0)
                    result.message = ' No messages found in queue'
                    self.rabbit_note = result.message
            return result

    def setPerformanceData(self, data, result, queue):

        if data.get('messages'):
                result.set_perf_data(queue + ".messages", data['messages'], warn=self.options.warning, crit=self.options.critical)
                result.set_perf_data(queue + ".rate", data['messages_details']['rate'])
                result.set_perf_data(queue + ".consumers", data['consumers'], crit='0')
        else:
                result.set_perf_data(queue + ".messages", 0, warn=self.options.warning, crit=self.options.critical)
                result.set_perf_data(queue + ".rate", 0)
                result.set_perf_data(queue + ".consumers", data['consumers'], crit='0')

        return result

    def check(self):
        """
        returns a response and perf data for this check
        """
        try:
            self.rabbit_error = 0
            self.rabbit_note = "action performed successfully"

            if not self.testOptions():
                return Response(UNKNOWN, "Incorrect check config" + self.rabbit_note)

            if not self.options.hostname or not self.options.port or not self.options.username or not self.options.password or not self.testOptions():
                return Response(UNKNOWN, "Incorrect missing options")

            if not self.makeUrl():
                return Response(UNKNOWN, "Error with URL")

            response = self.parseJson(self.doApiGet())

            for queue in response: 
                self.generateQueueUrl(queue["name"])

                if self.rabbit_error > 0:
                    return Response(CRITICAL, self.rabbit_note)

                data = self.parseJson(self.doApiGet())

                if self.rabbit_error > 0:
                    return Response(CRITICAL, self.rabbit_note)

                result = self.parseResult(data)

                self.setPerformanceData(data, result, queue["name"])
                print result
        except Exception as e:
            return Response(UNKNOWN, "Error occurred:" + str(e))


if __name__ == "__main__":
    obj = RabbitAllQueuesCheck()
    obj.check()

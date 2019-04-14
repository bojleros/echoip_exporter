#!/usr/bin/python3
from prometheus_client import start_http_server, Gauge
import json
import requests
import sys
import os
import time
import re
import signal
import sched
import datetime


def log(msg):
    print("[%s] : %s" % (str(datetime.datetime.now()), msg))


class Envconf():

    def __init__(self):

        c = {}
        e = os.environ

        c['server_url'] = e.get("SERVER_URL", "https://ifconfig.co")
        c['refresh_interval'] = int(e.get("REFRESH_INTERVAL", 60))
        c['refresh_timeout'] = float(e.get("REFRESH_TIMEOUT", 3))
        c['port'] = int(e.get("PORT", 19666))

        try:
            c['tests'] = json.loads(e.get("TESTS", "not JSON"))
        except Exception as e:
            log("Unable to load environmental TESTS, json expected : %s" % str(e))
            sys.exit(-2)

        if isinstance(c['tests'], dict) != True:
            log("Environmental TESTS is suposed to be an hash of hashes")
            sys.exit(-3)

        testsFields = ['field', 'test', 'value']

        for t in c['tests']:
            log("Parsing tests for %s" % str(t))

            l = list(set(testsFields) - set(c['tests'][t]))
            if len(l) > 0:
                log("Missing keys in test: %s" % str(t))
                sys.exit(-4)

        # todo: variable type and format validation

        self.conf = c


class Collector:

    def __init__(self, conf):
        self.conf = conf
        self.body = {}

        self.sched = False

        self.tests = {}

        self.last_refresh = Gauge("last_refresh_timestamp", "")
        self.last_refresh.set(-1)

        for t in self.conf['tests']:
            self.tests[t] = Gauge(str(t), "")
            self.tests[t].set(-1)

        self.process()
        start_http_server(self.conf['port'])

    def refresh(self):

        try:
            r = requests.get(self.conf['server_url'], timeout=self.conf[
                             'refresh_timeout'], headers={'Accept': 'application/json'})
            r.raise_for_status()
            r = r.content.decode('UTF-8')
            j = json.loads(r)
        except Exception as e:
            log("Refresh error : %s" % str(e))
            for t in self.conf['tests']:
                self.tests[t].set(-1)
            return False
        else:
            self.last_refresh.set(int(time.time()))
            self.body = j
            return True

    def evaluate(self):

        for t in self.conf['tests']:

            te = self.conf['tests'][t]

            if te['test'] == 'regex':
                if re.match(te['value'], self.body[te['field']]):
                    self.tests[t].set(1)
                else:
                    self.tests[t].set(0)

            if te['test'] == 'eq':
                if float(te['value']) == float(self.body[te['field']]):
                    self.tests[t].set(1)
                else:
                    self.tests[t].set(0)

            if te['test'] == 'gt':
                if float(te['value']) < float(self.body[te['field']]):
                    self.tests[t].set(1)
                else:
                    self.tests[t].set(0)

            if te['test'] == 'lt':
                if float(te['value']) > float(self.body[te['field']]):
                    self.tests[t].set(1)
                else:
                    self.tests[t].set(0)

            if te['test'] == 'inrange':
                thr = te['value'].split(':')

                if float(thr[0]) < float(self.body[te['field']]) and float(thr[1]) > float(self.body[te['field']]):
                    self.tests[t].set(1)
                else:
                    self.tests[t].set(0)

    def process(self):
        if bool(self.sched):
            self.sched.enter(self.conf['refresh_interval'], 1, self.process)

        if self.refresh():
            self.evaluate()
            log("Echoip endpoint refreshed")

    def start_pooling(self):
        self.sched = sched.scheduler(time.time, time.sleep)
        self.sched.enter(self.conf['refresh_interval'], 1, self.process)
        self.sched.run()

    def stop_pooling(self):
        if bool(self.sched):
            del self.sched
            self.sched = False


def killer(_signo, _stack_frame):
    log("Stopping on signal %s" % _signo)
    sys.exit(0)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, killer)
    signal.signal(signal.SIGTERM, killer)

    e = Envconf()
    c = Collector(e.conf)

    log("Running ...")

    c.start_pooling()

    signal.pause()

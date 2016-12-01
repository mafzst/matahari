from tests import *
from reporters import *

def getTests():
    tests = {}
    tests["PID"] = pid.PidTest
    tests["LOADAVG"] = hardware.LoadavgTest
    tests["PMEMORY"] = hardware.MemoryConsumptionTest
    tests["PING"] = network.PingTest
    tests["HTTP"] = network.HTTPErrorTest

    return tests

def getReporters():
    reporters = {}
    reporters["CACHETHQ-COMP"] = cachethq.ComponentReporter
    reporters["CACHETHQ-METR"] = cachethq.MetricReporter
    reporters["MAIL"] = mail.MailReporter

    return reporters

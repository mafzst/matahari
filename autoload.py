from runners import *
from reporters import *

def getRunners():
    runners = {}
    runners["PID"] = pid.PidTest
    runners["LOADAVG"] = hardware.LoadavgTest
    runners["PMEMORY"] = hardware.MemoryConsumptionTest
    runners["PING"] = network.PingTest
    runners["HTTP"] = network.HTTPErrorTest

    return runners

def getReporters():
    reporters = {}
    reporters["CACHETHQ-COMP"] = cachethq.ComponentReporter
    reporters["CACHETHQ-METR"] = cachethq.MetricReporter
    reporters["MAIL"] = mail.MailReporter

    return reporters

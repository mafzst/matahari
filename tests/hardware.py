import subprocess, re

class LoadavgTest:
    """
    LoadAverage tests class
    """

    def __init__(self, config, reporters, logger):
        """
        Test constructor
         - `config`: config object used in test
         - `reporters`: List of Reporter instances used to report test result
         - `logger`: Logger instance used to log operations
        """
        self.config = config
        self.reporters = reporters
        self.logger  = logger

    def test(self):
        """
        Run test. Report result to reports
        """
        process = subprocess.Popen(["cat",  "/proc/loadavg"], stdout = subprocess.PIPE)

        outs = subprocess.check_output(['awk', '{print $2}'], stdin = process.stdout)
        try:
            loadavg = float(outs)
        except:
            self.logger.testResult("LOAD", False, "Test error. Nothing reported")
        else:
            self.report(loadavg)
            self.logger.testResult("LOAD", True, loadavg)

    def report(self, result):
        reportersToCall = self.config["REPORTERS"].sections

        for reporter in reportersToCall:
            self.reporters[reporter].reportStatus(result, self.config["REPORTERS"][reporter])

class MemoryConsumptionTest:
    """
    Process memory consumption test class
    """

    def __init__(self, config, reporters, logger):
        """
        Test constructor
         - `config`: config object used in test
         - `reporters`: List of Reporter instances used to report test result
         - `logger`: Logger instance used to log operations
        """
        self.config = config
        self.reporters = reporters
        self.logger  = logger

    def test(self):
        process = subprocess.Popen(["pmap", "2125"], stdout = subprocess.PIPE)
        outs = subprocess.check_output(["grep", "total"], stdin = process.stdout)

        memory = re.findall(r'\d+', str(outs))

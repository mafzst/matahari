import subprocess

class PidTest:
    """
    PID tests class
    """

    def __init__(self, config, reporters, logger):
        """
        Test constructor
         - `config`: config object used in test
            - `processName`: System name of the process to be tested
            - `apiId`: Component ID in Cachet API
            - `okStatus`: Status to report if PID found
            - `errorStatus`: Status to report if PID not found
         - `reporters`: List of Reporter instances used to report test result
         - `logger`: Logger instance used to log operations
        """
        self.config = config
        self.reporters = reporters
        self.logger = logger

    def test(self):
        """
        Run test. Report result to reports
        """
        process = subprocess.Popen(["pgrep", self.config["processName"]], stdout = subprocess.PIPE)

        outs, err = process.communicate()
        try:
            pid = int(outs)
            self.report(True)
            self.logger.testResult("PID ", True, pid)
        except ValueError:
            self.report(False)
            self.logger.testResult("PID ", False, 'PID not found')
        except:
            self.logger.testResult("PID ", False, 'Test error. No status reported')

    def report(self, result):
        reportersToCall = self.config["REPORTERS"].sections

        for reporter in reportersToCall:
            self.reporters[reporter].reportStatus(result, self.config["REPORTERS"][reporter])

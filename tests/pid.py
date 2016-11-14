import subprocess

class PidTest:
    """
    PID tests class
    """

    @staticmethod
    def getName():
        return "PID"

    @staticmethod
    def test(container):
        """
        Run test. Report result to reports
        """
        process = subprocess.Popen(["pgrep", container.config["processName"]], stdout = subprocess.PIPE)

        outs, err = process.communicate()
        try:
            pid = int(outs)
            container.report(True)
            container.loggerInterface.testResult("PID ", True, pid)
        except ValueError:
            container.report(False)
            container.loggerInterface.testResult("PID ", False, 'PID not found')
        except:
            container.loggerInterface.testResult("PID ", False, 'Test error. No status reported')
            
        container.finish()

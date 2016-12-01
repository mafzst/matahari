from configobj import ConfigObj
import time, sys
from framework import Daemon, Logger, Core, initReporters
from autoload import getReporters

config = ConfigObj('matahari.conf')
logger = Logger(config["LOGGING"])
reporters = initReporters(getReporters(), config["REPORTERS"])

def runtime():
    logger.info('main', "App started")
    try:
        while True:
            pass
            logger.info('main', "Starting tests")
            for runner in config["RUNNERS"].sections:
                runnerConfig = config["RUNNERS"][runner]
                runnerConfig["logger"] = logger
                Core.executeRunner(runnerConfig, reporters)
            logger.info('main', "Tests finished: Going to sleep for 30s before next test")
            time.sleep(30)
    except KeyboardInterrupt:
        logger.logInterrupt('main', "Shutting down, bye :)")
    except:
        logger.logInterrupt('main', "Shutting down with ERRROR!")
        raise
    finally:
        config.write()

daemon = Daemon("/tmp/mathari.pid", runtime)
if len(sys.argv) > 1:
    if 'start' == sys.argv[1]:
            daemon.start()
    elif 'stop' == sys.argv[1]:
            daemon.stop()
    elif 'restart' == sys.argv[1]:
            daemon.restart()
    else:
            print("Unknown command")
            sys.exit(2)
else:
    runtime()
